from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.crawling.services.crawler import CrawlEngine, SSRFSecurityError
from apps.classification.services.date_extractor import DateExtractionService
from apps.geography.services.resolver import GeographyResolver
from apps.classification.services.classifier import StudyClassifier
from apps.opportunities.services.deduplicator import DeduplicationService
from apps.sources.models import Source
from apps.opportunities.models import OpportunityStatus, GeographyStatus
from .models import RawDocument

class ManualIngestionView(APIView):
    """
    Executes the complete 7-step inspection and classification pipeline on any given URL.
    Optionally persists the candidate into the database.
    """
    def post(self, request):
        url = request.data.get('url', '').strip()
        save_to_db = request.data.get('save_to_database', False)

        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        crawler = CrawlEngine()
        date_extractor = DateExtractionService()
        geo_resolver = GeographyResolver()
        classifier = StudyClassifier()

        try:
            # 1. Fetch
            fetch_res = crawler.fetch_page(url)
            # 2. Extract
            doc_data = crawler.parse_html_document(fetch_res['raw_content'], fetch_res['final_url'])

            title = doc_data['title'] or url
            text = doc_data['clean_text']
            meta = doc_data['meta_tags']

            # 3. Classify
            class_res = classifier.classify(title, text, meta)

            # 4. Extract Date
            date_res = date_extractor.extract_date(
                text_content=text,
                meta_tags=meta,
                json_ld=doc_data.get('json_ld')
            )

            # 5. Extract Geography
            geo_res = geo_resolver.resolve(
                title=title,
                text_content=text,
                eligibility_text=class_res.eligibility_summary,
                meta_tags=meta
            )

            # 6. Determine qualification
            # Must be research study, within 7 days, US/CA eligible
            is_fresh = False
            days_old = None
            if date_res.published_at:
                delta = datetime.now(timezone.utc) - date_res.published_at
                days_old = round(delta.total_seconds() / 86400, 2)
                is_fresh = 0 <= days_old <= 7.0

            qualifies = (
                class_res.is_research_opportunity and
                is_fresh and
                geo_res.is_eligible_us_or_ca and
                date_res.confidence >= 0.70 and
                geo_res.participant_geo_confidence >= 0.70
            )

            result_payload = {
                'url': url,
                'final_url': fetch_res['final_url'],
                'status_code': fetch_res['status_code'],
                'title': title,
                'canonical_url': doc_data['canonical_url'],
                'is_research_opportunity': class_res.is_research_opportunity,
                'study_type': class_res.study_type,
                'reward': class_res.reward_text,
                'duration': class_res.duration_text,
                'eligibility': class_res.eligibility_summary,
                'organization': class_res.organization,
                'published_at': date_res.published_at.isoformat() if date_res.published_at else None,
                'date_source': date_res.source,
                'date_precision': date_res.precision,
                'date_confidence': date_res.confidence,
                'days_old': days_old,
                'is_fresh_7_days': is_fresh,
                'geography_status': geo_res.geography_status,
                'geography_confidence': geo_res.participant_geo_confidence,
                'geography_matches': [m.to_dict() for m in geo_res.matches],
                'geographic_reason': geo_res.case_reason,
                'qualifies_for_alert': qualifies,
                'exclusion_reason': class_res.exclusion_reason or (
                    "Not fresh (older than 7 days)" if not is_fresh and date_res.published_at else
                    "Unknown publication date" if not date_res.published_at else
                    "Geography not eligible for US/Canada" if not geo_res.is_eligible_us_or_ca else ""
                ),
            }

            # 7. Optionally save
            if save_to_db:
                source, _ = Source.objects.get_or_create(
                    slug='manual-ingestion',
                    defaults={'name': 'Manual Ingestion', 'source_type': 'custom', 'base_url': 'http://localhost'}
                )

                raw_doc = RawDocument.objects.create(
                    source=source,
                    url=url,
                    canonical_url=doc_data['canonical_url'],
                    http_status=fetch_res['status_code'],
                    text_content=text[:5000],
                    content_hash=fetch_res['content_hash'],
                    metadata_json={'title': title, 'meta': meta}
                )

                deduplicator = DeduplicationService()
                opp_status = OpportunityStatus.ELIGIBLE if qualifies else OpportunityStatus.VERIFIED if class_res.is_research_opportunity else OpportunityStatus.EXCLUDED

                opp, is_new, dec_reason = deduplicator.record_opportunity(
                    opportunity_data={
                        'title': title,
                        'description': text[:1000],
                        'study_type': class_res.study_type,
                        'source_url': url,
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
                        'exclusion_reason': result_payload['exclusion_reason'],
                        'content_hash': fetch_res['content_hash'],
                    },
                    source=source,
                    raw_document=raw_doc
                )
                result_payload['saved_opportunity_id'] = str(opp.id)
                result_payload['deduplication_result'] = dec_reason

            return Response(result_payload, status=status.HTTP_200_OK)

        except SSRFSecurityError as e:
            return Response({'error': f"Security policy blocked URL: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Ingestion error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
