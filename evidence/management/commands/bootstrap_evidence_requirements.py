import csv
from django.core.management.base import BaseCommand
from indicators.models import Indicator
from evidence.models import EvidenceRequirement
from core.constants import EvidenceType, DocumentType, RecurrenceMode

class Command(BaseCommand):
    help = 'Bootstrap initial evidence requirements from CSV or defaults'

    def handle(self, *args, **kwargs):
        csv_file = 'data/source_materials/test-export_framework_template_FIXED.csv'
        created_count = 0
        
        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                indicator_no = row['indicator_code']
                try:
                    indicator = Indicator.objects.get(indicator_no=indicator_no)
                except Indicator.DoesNotExist:
                    continue
                
                evidence_type = row.get('evidence_type', EvidenceType.OTHER)
                if not evidence_type or evidence_type not in EvidenceType.values:
                    evidence_type = EvidenceType.OTHER
                    
                document_type = row.get('document_type', DocumentType.OTHER)
                if not document_type or document_type not in DocumentType.values:
                    document_type = DocumentType.OTHER
                
                recurrence_mode = row.get('recurrence_mode', RecurrenceMode.NONE)
                if not recurrence_mode or recurrence_mode not in RecurrenceMode.values:
                    recurrence_mode = RecurrenceMode.NONE
                
                min_count = 1
                try:
                    min_count = int(row.get('minimum_required_evidence_count', 1))
                except ValueError:
                    pass
                
                title = f"Evidence for {indicator_no}"
                
                # Check if requirement already exists for this indicator
                if not EvidenceRequirement.objects.filter(indicator=indicator).exists():
                    EvidenceRequirement.objects.create(
                        indicator=indicator,
                        title=title,
                        description=row.get('required_evidence_description', ''),
                        evidence_type=evidence_type,
                        document_type=document_type,
                        recurrence_mode=recurrence_mode,
                        recurrence_frequency=row.get('recurrence_frequency', ''),
                        minimum_required_count=min_count,
                        template_reusable=row.get('reusable_template_allowed', 'False') == 'True',
                        evidence_reuse_policy=row.get('evidence_reuse_policy', '')
                    )
                    created_count += 1
                    
        # Add fallback default evidence requirement if an indicator has none.
        for indicator in Indicator.objects.all():
            if not EvidenceRequirement.objects.filter(indicator=indicator).exists():
                EvidenceRequirement.objects.create(
                    indicator=indicator,
                    title=f"General Evidence for {indicator.indicator_no}",
                    evidence_type=EvidenceType.OTHER,
                    document_type=DocumentType.OTHER
                )
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully bootstrapped {created_count} evidence requirements.'))
