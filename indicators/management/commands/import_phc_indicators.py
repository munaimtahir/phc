import csv
import os
from django.core.management.base import BaseCommand
from indicators.models import Indicator, IndicatorCompliance

class Command(BaseCommand):
    help = 'Imports PHC indicators from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        total_imported = 0
        duplicates = 0
        
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                indicator_no = row.get('indicator_code', '').strip()
                if not indicator_no:
                    continue
                
                # Check for uniqueness or update
                indicator, created = Indicator.objects.update_or_create(
                    indicator_no=indicator_no,
                    defaults={
                        'functional_area_code': row.get('area_code', '').strip(),
                        'functional_area_name': row.get('area_name', '').strip(),
                        'standard_code': row.get('standard_code', '').strip(),
                        'standard_title': row.get('standard_name', '').strip(),
                        'indicator_text': row.get('indicator_text', '').strip(),
                        'compliance_requirement': row.get('fulfillment_guidance', '').strip(),
                        'required_evidence': row.get('required_evidence_description', '').strip(),
                        'evidence_category': row.get('evidence_type', '').strip(),
                        'recurring_required': str(row.get('is_recurring', '')).strip().lower() in ['true', 'yes', '1'],
                        'recurrence_frequency': row.get('recurrence_frequency', '').strip(),
                        'is_locked': True,
                    }
                )
                
                if created:
                    total_imported += 1
                else:
                    duplicates += 1

                # Ensure compliance row exists
                IndicatorCompliance.objects.get_or_create(indicator=indicator)
        
        total_count = Indicator.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {total_imported} new indicators.'))
        self.stdout.write(self.style.SUCCESS(f'Updated {duplicates} existing indicators.'))
        self.stdout.write(self.style.SUCCESS(f'Total indicators in database: {total_count}'))
        
        if total_count == 118:
            self.stdout.write(self.style.SUCCESS('Count matches exactly 118 indicators as expected.'))
        else:
            self.stdout.write(self.style.WARNING(f'Warning: Expected 118 indicators, but found {total_count}.'))
            
        # Distribution
        areas = Indicator.objects.values_list('functional_area_code', flat=True).distinct()
        self.stdout.write(f"\nFunctional Areas distribution: {areas.count()} areas")
