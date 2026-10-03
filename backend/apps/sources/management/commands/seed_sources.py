from django.core.management.base import BaseCommand
from apps.sources.models import Source, SourceType, DiscoveryQuery

class Command(BaseCommand):
    help = 'Seeds initial permitted, compliant research discovery sources and queries.'

    def handle(self, *args, **options):
        initial_sources = [
            {
                'name': 'Harvard Decision Science Laboratory',
                'slug': 'harvard-dsl',
                'source_type': SourceType.UNIVERSITY,
                'base_url': 'https://dsl.harvard.edu',
                'feed_or_api_url': 'https://dsl.harvard.edu/participate',
                'crawl_interval_seconds': 7200,
                'compliance_notes': 'Public participant recruitment page of Harvard Decision Science Lab.',
                'is_active': True,
            },
            {
                'name': 'Stanford Behavioral Lab Recruitment',
                'slug': 'stanford-behavioral-lab',
                'source_type': SourceType.UNIVERSITY,
                'base_url': 'https://behaviorallab.stanford.edu',
                'feed_or_api_url': 'https://behaviorallab.stanford.edu/participate',
                'crawl_interval_seconds': 7200,
                'compliance_notes': 'Public research participant recruitment directory.',
                'is_active': True,
            },
            {
                'name': 'Reddit Paid Studies (Public RSS)',
                'slug': 'reddit-paid-studies',
                'source_type': SourceType.RSS,
                'base_url': 'https://www.reddit.com/r/PaidStudies',
                'feed_or_api_url': 'https://www.reddit.com/r/PaidStudies/.rss',
                'crawl_interval_seconds': 1800,
                'compliance_notes': 'Public Reddit RSS feed for participant recruitment.',
                'is_active': True,
            },
            {
                'name': 'ClinicalTrials.gov Public API (US/Canada Recruiting Studies)',
                'slug': 'clinicaltrials-gov',
                'source_type': SourceType.API,
                'base_url': 'https://clinicaltrials.gov',
                'feed_or_api_url': 'https://clinicaltrials.gov/api/v2/studies?filter.overallStatus=RECRUITING&query.locn=United+States',
                'crawl_interval_seconds': 14400,
                'compliance_notes': 'Official public API of ClinicalTrials.gov with rate limit compliance.',
                'is_active': True,
            },
        ]

        created_sources = 0
        for src_data in initial_sources:
            slug = src_data.pop('slug')
            _, created = Source.objects.get_or_create(slug=slug, defaults=src_data)
            if created:
                created_sources += 1

        # Seed discovery queries (Section 29)
        queries = [
            ("paid research study Arizona", "paid_study"),
            ("participants needed Ontario", "recruitment"),
            ("user research Toronto", "ux_research"),
            ("survey participants California", "paid_survey"),
            ("focus group United States", "focus_group"),
            ("clinical study participants Canada", "clinical_study"),
            ("usability testing remote US", "usability"),
            ("market research interview Phoenix", "market_research"),
        ]

        created_queries = 0
        for query_text, cat in queries:
            _, created = DiscoveryQuery.objects.get_or_create(
                query_text=query_text,
                defaults={'category': cat, 'is_active': True}
            )
            if created:
                created_queries += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {created_sources} sources and {created_queries} discovery queries."
        ))
