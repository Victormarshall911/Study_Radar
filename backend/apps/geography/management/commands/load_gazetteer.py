import json
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.geography.models import Geography, GeographyScope

class Command(BaseCommand):
    help = 'Seeds the database with canonical US states, Canadian provinces, territories, and major cities from canonical_gazetteer.json'

    def handle(self, *args, **options):
        data_path = Path(__file__).resolve().parent.parent.parent / 'data' / 'canonical_gazetteer.json'
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        created_count = 0

        # Seed US Nationwide
        Geography.objects.get_or_create(
            country='US',
            scope=GeographyScope.NATIONWIDE,
            defaults={
                'is_us': True,
                'aliases': ['USA', 'United States', 'US nationwide', 'US residents only']
            }
        )
        created_count += 1

        # Seed Canada Nationwide
        Geography.objects.get_or_create(
            country='CA',
            scope=GeographyScope.NATIONWIDE,
            defaults={
                'is_ca': True,
                'aliases': ['Canada', 'Canadian', 'Canada-wide', 'across Canada']
            }
        )
        created_count += 1

        # Seed US States
        for state in data.get('us_states', []):
            st_obj, _ = Geography.objects.get_or_create(
                country='US',
                state_province=state['name'],
                state_code=state['code'],
                scope=GeographyScope.STATE,
                defaults={
                    'is_us': True,
                    'aliases': [state['name'], state['code']] + state.get('regions', []) + state.get('metro', [])
                }
            )
            created_count += 1

            for city in state.get('cities', []):
                Geography.objects.get_or_create(
                    country='US',
                    state_province=state['name'],
                    state_code=state['code'],
                    city=city,
                    scope=GeographyScope.CITY,
                    defaults={'is_us': True, 'aliases': [city, f"{city}, {state['code']}"]}
                )
                created_count += 1

        # Seed Canadian Provinces & Territories
        for prov in data.get('ca_provinces', []):
            Geography.objects.get_or_create(
                country='CA',
                state_province=prov['name'],
                state_code=prov['code'],
                scope=GeographyScope.PROVINCE,
                defaults={'is_ca': True, 'aliases': [prov['name'], prov['code']]}
            )
            created_count += 1
            for city in prov.get('cities', []):
                Geography.objects.get_or_create(
                    country='CA',
                    state_province=prov['name'],
                    state_code=prov['code'],
                    city=city,
                    scope=GeographyScope.CITY,
                    defaults={'is_ca': True, 'aliases': [city, f"{city}, {prov['code']}"]}
                )
                created_count += 1

        for terr in data.get('ca_territories', []):
            Geography.objects.get_or_create(
                country='CA',
                state_province=terr['name'],
                state_code=terr['code'],
                scope=GeographyScope.TERRITORY,
                defaults={'is_ca': True, 'aliases': [terr['name'], terr['code']]}
            )
            created_count += 1
            for city in terr.get('cities', []):
                Geography.objects.get_or_create(
                    country='CA',
                    state_province=terr['name'],
                    state_code=terr['code'],
                    city=city,
                    scope=GeographyScope.CITY,
                    defaults={'is_ca': True, 'aliases': [city, f"{city}, {terr['code']}"]}
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded/verified canonical gazetteer records. Processed: {created_count}"))
