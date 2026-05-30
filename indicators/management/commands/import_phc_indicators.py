import csv
from django.core.management.base import BaseCommand
from indicators.models import Indicator

class Command(BaseCommand):
    help = 'Import PHC indicators from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            created_count = 0
            updated_count = 0
            
            for row in reader:
                indicator_no = row['indicator_code']
                
                defaults = {
                    'functional_area_code': row['area_code'],
                    'functional_area_name': row['area_name'],
                    'standard_no': row['standard_code'],
                    'standard_code': row['standard_code'],
                    'standard_title': row['standard_name'],
                    'indicator_text': row['indicator_text'],
                    'compliance_requirement': row.get('required_evidence_description', ''),
                    'surveyor_check': row.get('fulfillment_guidance', ''),
                    'is_locked': True
                }
                
                ind, created = Indicator.objects.update_or_create(
                    indicator_no=indicator_no,
                    defaults=defaults
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
        self.stdout.write(self.style.SUCCESS(f'Successfully imported indicators. Created: {created_count}, Updated: {updated_count}'))
