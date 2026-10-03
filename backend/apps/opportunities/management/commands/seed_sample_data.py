from datetime import datetime, timezone, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.opportunities.models import Opportunity, OpportunityStatus, GeographyStatus, StudyType, DatePrecision, OpportunityGeography
from apps.geography.models import Geography, GeographyScope
from apps.sources.models import Source

class Command(BaseCommand):
    help = 'Seeds realistic sample research studies in US & Canada conforming to instruction.md'

    def handle(self, *args, **options):
        now = datetime.now(timezone.utc)

        source, _ = Source.objects.get_or_create(
            slug='harvard-dsl',
            defaults={'name': 'Harvard Decision Science Lab', 'base_url': 'https://dsl.harvard.edu'}
        )

        samples = [
            {
                'title': 'Cognitive AI Interaction & Workflow Usability Study',
                'description': 'A 45-minute remote research interview exploring how professionals interact with generative AI tools in daily workflows.',
                'study_type': StudyType.USER_INTERVIEW,
                'organization': 'MIT & Harvard Collaborative Research',
                'source_url': 'https://dsl.harvard.edu/studies/ai-workflow-2026',
                'application_url': 'https://dsl.harvard.edu/apply/ai-workflow',
                'published_at': now - timedelta(hours=3),
                'published_date_precision': DatePrecision.RELATIVE_DATETIME,
                'date_confidence': 0.98,
                'date_source': 'text_pattern',
                'reward_amount': Decimal('75.00'),
                'reward_currency': 'USD',
                'reward_text': '$75 Amazon Gift Card',
                'is_paid': True,
                'duration_minutes': 45,
                'duration_text': '45 minutes',
                'eligibility_text': 'Adults 18+ in Phoenix and across Arizona who use AI tools regularly.',
                'geography_status': GeographyStatus.US_ELIGIBLE,
                'participant_geo_confidence': 0.96,
                'status': OpportunityStatus.ELIGIBLE,
                'content_hash': 'hash_sample_phoenix_1',
                'geo_query': {'country': 'US', 'state_province': 'Arizona', 'city': 'Phoenix'},
            },
            {
                'title': 'Greater Toronto Area Commuter Experience Survey',
                'description': 'Evaluating urban transit patterns and micro-mobility across Ontario and the GTA.',
                'study_type': StudyType.PAID_SURVEY,
                'organization': 'University of Toronto Transportation Lab',
                'source_url': 'https://utoronto.ca/trans-lab/survey-2026',
                'application_url': 'https://utoronto.ca/trans-lab/participate',
                'published_at': now - timedelta(days=1, hours=4),
                'published_date_precision': DatePrecision.RELATIVE_DATE,
                'date_confidence': 0.95,
                'date_source': 'json_ld',
                'reward_amount': Decimal('40.00'),
                'reward_currency': 'CAD',
                'reward_text': 'CAD $40 Interac E-transfer',
                'is_paid': True,
                'duration_minutes': 20,
                'duration_text': '20 minutes',
                'eligibility_text': 'Residents of Ontario living or working in the Greater Toronto Area.',
                'geography_status': GeographyStatus.CA_ELIGIBLE,
                'participant_geo_confidence': 0.97,
                'status': OpportunityStatus.ELIGIBLE,
                'content_hash': 'hash_sample_toronto_2',
                'geo_query': {'country': 'CA', 'state_province': 'Ontario', 'city': 'Toronto'},
            },
            {
                'title': 'Nationwide Digital Health & Wearable Usability Study',
                'description': 'Testing a new sleep & heart rate monitoring mobile companion application.',
                'study_type': StudyType.USABILITY_TEST,
                'organization': 'Stanford Digital Health Institute',
                'source_url': 'https://stanford.edu/health-lab/wearables',
                'application_url': 'https://stanford.edu/health-lab/apply',
                'published_at': now - timedelta(days=2, hours=8),
                'published_date_precision': DatePrecision.EXACT_DATE,
                'date_confidence': 0.94,
                'date_source': 'meta_tag',
                'reward_amount': Decimal('100.00'),
                'reward_currency': 'USD',
                'reward_text': '$100 Direct Deposit',
                'is_paid': True,
                'duration_minutes': 60,
                'duration_text': '60 minutes',
                'eligibility_text': 'Adults across the United States with an iOS or Android smartphone.',
                'geography_status': GeographyStatus.US_ELIGIBLE,
                'participant_geo_confidence': 0.98,
                'status': OpportunityStatus.ELIGIBLE,
                'content_hash': 'hash_sample_us_nationwide_3',
                'geo_query': {'country': 'US', 'scope': GeographyScope.NATIONWIDE},
            },
            {
                'title': 'Canadian Bilingual Consumer Retail Focus Group',
                'description': 'Virtual roundtable discussion on consumer product labeling and shopping habits.',
                'study_type': StudyType.FOCUS_GROUP,
                'organization': 'McGill Consumer Behaviour Lab',
                'source_url': 'https://mcgill.ca/consumer-lab/retail-focus',
                'application_url': 'https://mcgill.ca/consumer-lab/register',
                'published_at': now - timedelta(days=3),
                'published_date_precision': DatePrecision.EXACT_DATE,
                'date_confidence': 0.92,
                'date_source': 'text_pattern',
                'reward_amount': Decimal('85.00'),
                'reward_currency': 'CAD',
                'reward_text': 'CAD $85 Prepaid Visa Card',
                'is_paid': True,
                'duration_minutes': 75,
                'duration_text': '75 minutes',
                'eligibility_text': 'Adults living anywhere in Canada (Quebec, Ontario, BC, and all provinces).',
                'geography_status': GeographyStatus.CA_ELIGIBLE,
                'participant_geo_confidence': 0.95,
                'status': OpportunityStatus.ELIGIBLE,
                'content_hash': 'hash_sample_canada_wide_4',
                'geo_query': {'country': 'CA', 'scope': GeographyScope.NATIONWIDE},
            },
            {
                'title': 'Clean Energy & Smart Thermostat Diary Study',
                'description': 'A 7-day diary logging household energy thermostat adjustments and comfort levels.',
                'study_type': StudyType.DIARY_STUDY,
                'organization': 'Berkeley Energy Resources Group',
                'source_url': 'https://berkeley.edu/energy/thermostat-diary',
                'application_url': 'https://berkeley.edu/energy/apply',
                'published_at': now - timedelta(days=5),
                'published_date_precision': DatePrecision.EXACT_DATE,
                'date_confidence': 0.90,
                'date_source': 'json_ld',
                'reward_amount': Decimal('120.00'),
                'reward_currency': 'USD',
                'reward_text': '$120 Virtual Visa',
                'is_paid': True,
                'duration_minutes': 30,
                'duration_text': '5 mins/day for 7 days',
                'eligibility_text': 'Residents of California and Texas with smart thermostats.',
                'geography_status': GeographyStatus.US_ELIGIBLE,
                'participant_geo_confidence': 0.95,
                'status': OpportunityStatus.ELIGIBLE,
                'content_hash': 'hash_sample_ca_tx_5',
                'geo_query': {'country': 'US', 'state_province': 'California'},
            },
            {
                'title': 'Archived Longitudinal Memory Study (Older than 7 Days)',
                'description': 'Historical study record demonstrating proper exclusion from fresh feeds.',
                'study_type': StudyType.ACADEMIC_SURVEY,
                'organization': 'Columbia University Psychology',
                'source_url': 'https://columbia.edu/psych/memory-study-old',
                'application_url': 'https://columbia.edu/psych/apply',
                'published_at': now - timedelta(days=22),
                'published_date_precision': DatePrecision.EXACT_DATE,
                'date_confidence': 0.95,
                'date_source': 'meta_tag',
                'reward_amount': Decimal('30.00'),
                'reward_currency': 'USD',
                'reward_text': '$30 Check',
                'is_paid': True,
                'duration_minutes': 40,
                'duration_text': '40 minutes',
                'eligibility_text': 'US residents only.',
                'geography_status': GeographyStatus.US_ELIGIBLE,
                'participant_geo_confidence': 0.95,
                'status': OpportunityStatus.EXPIRED,
                'content_hash': 'hash_sample_old_6',
                'geo_query': {'country': 'US', 'scope': GeographyScope.NATIONWIDE},
            }
        ]

        count = 0
        for s in samples:
            geo_query = s.pop('geo_query')
            title = s['title']
            opp, created = Opportunity.objects.get_or_create(
                title=title,
                defaults=s
            )
            if created:
                count += 1
                # Link geography
                geo = Geography.objects.filter(**geo_query).first()
                if geo:
                    OpportunityGeography.objects.create(
                        opportunity=opp,
                        geography=geo,
                        scope=geo.scope,
                        confidence=0.98
                    )

        self.stdout.write(self.style.SUCCESS(f"Seeded {count} realistic research opportunities."))
