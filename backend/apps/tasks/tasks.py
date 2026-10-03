import logging
from datetime import datetime, timezone, timedelta
from celery import shared_task
from django.conf import settings
from apps.sources.models import Source, SourceRun, SourceRunStatus
from apps.crawling.models import RawDocument
from apps.crawling.services.crawler import CrawlEngine
from apps.classification.services.date_extractor import DateExtractionService
from apps.geography.services.resolver import GeographyResolver
from apps.classification.services.classifier import StudyClassifier
from apps.opportunities.services.deduplicator import DeduplicationService
from apps.opportunities.models import Opportunity, OpportunityStatus, GeographyStatus
from apps.notifications.services import NotificationDispatcher

logger = logging.getLogger(__name__)

@shared_task
def crawl_single_source_task(source_id: str):
    """
    Crawls a configured source connector, extracts candidates, runs the pipeline,
    and records results with full run observability.
    """
    try:
        source = Source.objects.get(id=source_id)
    except Source.DoesNotExist:
        logger.error(f"Source {source_id} not found.")
        return

    run = SourceRun.objects.create(source=source, status=SourceRunStatus.RUNNING)
    start_time = datetime.now(timezone.utc)

    crawler = CrawlEngine(rate_limit_rps=source.rate_limit_rps)
    classifier = StudyClassifier()
    date_extractor = DateExtractionService()
    geo_resolver = GeographyResolver()
    deduplicator = DeduplicationService()
    dispatcher = NotificationDispatcher()

    items_fetched = 0
    items_parsed = 0
    items_accepted = 0
    items_rejected = 0
    duplicate_count = 0

    try:
        # Fetch the target feed or page
        target_url = source.feed_or_api_url or source.base_url
        page_res = crawler.fetch_page(target_url)
        items_fetched += 1

        raw_doc = RawDocument.objects.create(
            source=source,
            source_run=run,
            url=target_url,
            canonical_url=page_res.get('final_url', target_url),
            http_status=page_res['status_code'],
            content_type=page_res['content_type'],
            content_hash=page_res['content_hash'],
            text_content=page_res['raw_content'][:10000]
        )

        doc_data = crawler.parse_html_document(page_res['raw_content'], page_res['final_url'])
        items_parsed += 1

        title = doc_data['title'] or source.name
        text = doc_data['clean_text']
        meta = doc_data['meta_tags']

        # Classify
        class_res = classifier.classify(title, text, meta)
        if not class_res.is_research_opportunity:
            items_rejected += 1
            run.status = SourceRunStatus.SUCCESS
            run.items_fetched = items_fetched
            run.items_parsed = items_parsed
            run.items_rejected = items_rejected
            run.finished_at = datetime.now(timezone.utc)
            run.save()
            return

        # Date & Geography
        date_res = date_extractor.extract_date(text_content=text, meta_tags=meta, json_ld=doc_data.get('json_ld'))
        geo_res = geo_resolver.resolve(title=title, text_content=text, eligibility_text=class_res.eligibility_summary, meta_tags=meta)

        is_fresh = False
        if date_res.published_at:
            delta = datetime.now(timezone.utc) - date_res.published_at
            is_fresh = 0 <= delta.total_seconds() <= (settings.FRESHNESS_WINDOW_DAYS * 86400)

        qualifies = (
            class_res.is_research_opportunity and
            is_fresh and
            geo_res.is_eligible_us_or_ca and
            date_res.confidence >= settings.CONFIDENCE_THRESHOLD_DATE and
            geo_res.participant_geo_confidence >= settings.CONFIDENCE_THRESHOLD_GEO
        )

        opp_status = OpportunityStatus.ELIGIBLE if qualifies else OpportunityStatus.VERIFIED

        opp, is_new, dec_reason = deduplicator.record_opportunity(
            opportunity_data={
                'title': title,
                'description': text[:1000],
                'study_type': class_res.study_type,
                'source_url': target_url,
                'canonical_url': doc_data['canonical_url'],
                'organization': class_res.organization,
                'published_at': date_res.published_at,
                'published_date_precision': date_res.precision,
                'date_source': date_res.source,
                'date_confidence': date_res.confidence,
                'reward_amount': class_res.reward_amount,
                'reward_currency': class_res.reward_currency,
                'reward_text': class_res.reward_text,
                'reward_type': class_res.reward_type,
                'is_paid': class_res.is_paid,
                'duration_minutes': class_res.duration_minutes,
                'duration_text': class_res.duration_text,
                'eligibility_text': class_res.eligibility_summary,
                'geography_status': geo_res.geography_status,
                'participant_geo_confidence': geo_res.participant_geo_confidence,
                'status': opp_status,
                'content_hash': page_res['content_hash'],
            },
            source=source,
            raw_document=raw_doc
        )

        if is_new:
            items_accepted += 1
            if qualifies and opp.is_eligible_for_alert:
                dispatcher.dispatch_for_opportunity(opp)
        else:
            duplicate_count += 1

        run.status = SourceRunStatus.SUCCESS
        run.items_fetched = items_fetched
        run.items_parsed = items_parsed
        run.items_accepted = items_accepted
        run.items_rejected = items_rejected
        run.duplicate_count = duplicate_count
        run.finished_at = datetime.now(timezone.utc)
        run.response_time_ms = (run.finished_at - start_time).total_seconds() * 1000
        run.save()

        source.last_run_at = run.finished_at
        source.last_success_at = run.finished_at
        source.status = 'idle'
        source.save(update_fields=['last_run_at', 'last_success_at', 'status'])

    except Exception as e:
        logger.error(f"Error during crawl of {source.name}: {str(e)}", exc_info=True)
        run.status = SourceRunStatus.FAILED
        run.error_message = str(e)
        run.finished_at = datetime.now(timezone.utc)
        run.save()

        source.failure_count += 1
        source.status = 'failing'
        source.save(update_fields=['failure_count', 'status'])

@shared_task
def schedule_all_active_sources():
    """Iterates through all active sources and triggers crawling."""
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        crawl_single_source_task.delay(str(source.id))

@shared_task
def cleanup_expired_opportunities():
    """
    Section 28: Moves opportunities older than 7 days from ELIGIBLE to EXPIRED.
    Retains them in the database for analytics without sending alerts.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.FRESHNESS_WINDOW_DAYS)
    updated = Opportunity.objects.filter(
        status__in=[OpportunityStatus.ELIGIBLE, OpportunityStatus.VERIFIED],
        published_at__lt=cutoff
    ).update(status=OpportunityStatus.EXPIRED)
    logger.info(f"Cleaned up {updated} expired opportunities.")
    return updated
