from django.core.management.base import BaseCommand
from django.db import transaction
from evidence.models import DocumentBatch, PlannedEvidenceDocument, Indicator
from core.constants import Priority, BatchType, DocumentKind, EvidenceNature, RecurrenceFrequency

class Command(BaseCommand):
    help = 'Seed standard document batches and planned evidence documents.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing batches and documents instead of skipping them.',
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed document batches and planned documents...'))
        
        # 1. Define standard batches
        batches_data = [
            {
                'code': 'GOV', 'name': 'Management & Governance Pack', 'priority': Priority.HIGH,
                'batch_type': BatchType.GOVERNANCE, 'functional_area': 'ROM', 'sequence_order': 1,
                'description': 'Leadership, policy, and organizational governance controls.'
            },
            {
                'code': 'FMS', 'name': 'Facility, Safety & Emergency Pack', 'priority': Priority.HIGH,
                'batch_type': BatchType.SAFETY_EMERGENCY, 'functional_area': 'FMS', 'sequence_order': 2,
                'description': 'Facility management, safety protocols, and emergency readiness.'
            },
            {
                'code': 'HRM', 'name': 'Human Resource Pack', 'priority': Priority.MEDIUM,
                'batch_type': BatchType.HUMAN_RESOURCE, 'functional_area': 'HRM', 'sequence_order': 3,
                'description': 'Staff management, qualifications, and records.'
            },
            {
                'code': 'MER', 'name': 'Equipment & Reagent Management Pack', 'priority': Priority.HIGH,
                'batch_type': BatchType.EQUIPMENT_REAGENT, 'functional_area': 'MER', 'sequence_order': 4,
                'description': 'Procurement, maintenance, and inventory of lab equipment and reagents.'
            },
            {
                'code': 'RRS', 'name': 'Recording & Reporting Pack', 'priority': Priority.MEDIUM,
                'batch_type': BatchType.RECORDING_REPORTING, 'functional_area': 'RRS', 'sequence_order': 5,
                'description': 'Patient records, reporting procedures, and data management.'
            },
            {
                'code': 'QA', 'name': 'Quality Assurance Pack', 'priority': Priority.HIGH,
                'batch_type': BatchType.QUALITY_ASSURANCE, 'functional_area': 'QA', 'sequence_order': 6,
                'description': 'Internal and external quality control, process monitoring, and CAPA.'
            },
            {
                'code': 'BSBS', 'name': 'Biosafety, Biosecurity & Waste Pack', 'priority': Priority.HIGH,
                'batch_type': BatchType.BIOSAFETY_WASTE, 'functional_area': 'BSBS', 'sequence_order': 7,
                'description': 'Biological safety, spill management, and healthcare waste disposal.'
            },
            {
                'code': 'PATIENT', 'name': 'Patient Rights, Access & Complaints Pack', 'priority': Priority.MEDIUM,
                'batch_type': BatchType.PATIENT_RIGHTS_ACCESS, 'functional_area': 'PRE', 'sequence_order': 8,
                'description': 'Accessibility, patient rights, tariffs, and complaint management.'
            },
        ]

        batch_objs = {}
        for b in batches_data:
            batch, created = DocumentBatch.objects.update_or_create(
                code=b['code'],
                defaults={
                    'name': b['name'], 'priority': b['priority'], 'batch_type': b['batch_type'],
                    'functional_area': b['functional_area'], 'sequence_order': b['sequence_order'],
                    'description': b['description']
                }
            )
            batch_objs[b['code']] = batch
            if created:
                self.stdout.write(f"Created batch: {batch.name}")

        # 2. Define planned documents
        planned_docs = [
            # GOV
            {
                'code': 'DOC-GOV-01', 'title': 'Mission Statement', 'batch': 'GOV',
                'document_kind': DocumentKind.DISPLAY_NOTICE, 'evidence_nature': EvidenceNature.ONE_TIME,
                'upload_needed': True, 'display_confirmation_needed': True, 'physical_confirmation_needed': True,
                'indicators': ['IND-007'], 'description': 'The official lab mission statement.'
            },
            {
                'code': 'DOC-GOV-02', 'title': 'Laboratory Organogram', 'batch': 'GOV',
                'document_kind': DocumentKind.DISPLAY_NOTICE, 'evidence_nature': EvidenceNature.ONE_TIME,
                'upload_needed': True, 'display_confirmation_needed': True, 'physical_confirmation_needed': True,
                'indicators': ['IND-011'], 'description': 'Organizational chart showing hierarchy.'
            },
            {
                'code': 'DOC-GOV-03', 'title': 'Policy and SOP Master Index', 'batch': 'GOV',
                'document_kind': DocumentKind.LIST_ROSTER, 'evidence_nature': EvidenceNature.ONE_TIME,
                'indicators': ['IND-013'], 'description': 'Master list of all laboratory policies and procedures.'
            },
            
            # FMS
            {
                'code': 'DOC-FMS-01', 'title': 'Fire and Non-Fire Emergency SOP', 'batch': 'FMS',
                'document_kind': DocumentKind.SOP, 'evidence_nature': EvidenceNature.ONE_TIME,
                'staff_awareness_needed': True, 'indicators': ['IND-019', 'IND-020', 'IND-021'],
                'description': 'Standard operating procedures for various emergencies.'
            },
            {
                'code': 'DOC-FMS-02', 'title': 'Mock Drill Report Form', 'batch': 'FMS',
                'document_kind': DocumentKind.REPORT, 'evidence_nature': EvidenceNature.RECURRING,
                'frequency': RecurrenceFrequency.ANNUAL, 'upload_needed': True, 'register_entry_needed': True,
                'indicators': ['IND-023'], 'description': 'Form for recording periodic mock drills.'
            },
            {
                'code': 'DOC-FMS-03', 'title': 'Staff Emergency Training Record', 'batch': 'FMS',
                'document_kind': DocumentKind.TRAINING_RECORD, 'evidence_nature': EvidenceNature.RECURRING,
                'frequency': RecurrenceFrequency.ANNUAL, 'staff_awareness_needed': True,
                'indicators': ['IND-024'], 'description': 'Records of training provided to staff regarding emergency procedures.'
            },

            # HRM
            {
                'code': 'DOC-HRM-01', 'title': 'Staff Job Descriptions', 'batch': 'HRM',
                'document_kind': DocumentKind.APPOINTMENT_ORDER, 'evidence_nature': EvidenceNature.ONE_TIME,
                'indicators': ['IND-025'], 'description': 'Job descriptions for all categories of staff.'
            },
            {
                'code': 'DOC-HRM-02', 'title': 'Staff Eligibility Criteria', 'batch': 'HRM',
                'document_kind': DocumentKind.POLICY, 'evidence_nature': EvidenceNature.ONE_TIME,
                'indicators': ['IND-026'], 'description': 'Criteria defining required qualifications for each role.'
            },
            {
                'code': 'DOC-HRM-03', 'title': 'Personal File Checklist', 'batch': 'HRM',
                'document_kind': DocumentKind.CHECKLIST, 'evidence_nature': EvidenceNature.ONE_TIME,
                'indicators': ['IND-036', 'IND-038', 'IND-039', 'IND-040'],
                'description': 'Checklist for maintaining standardized personal files for all employees.'
            },

            # MER
            {
                'code': 'DOC-MER-01', 'title': 'Reagent Storage and Use SOP', 'batch': 'MER',
                'document_kind': DocumentKind.SOP, 'evidence_nature': EvidenceNature.ONE_TIME,
                'indicators': ['IND-045', 'IND-046', 'IND-047', 'IND-048'],
                'description': 'Procedures for receiving, storing, and utilizing reagents.'
            },
            {
                'code': 'DOC-MER-02', 'title': 'Equipment Logbook Template', 'batch': 'MER',
                'document_kind': DocumentKind.LOGBOOK, 'evidence_nature': EvidenceNature.RECURRING,
                'frequency': RecurrenceFrequency.DAILY, 'register_entry_needed': True,
                'indicators': ['IND-049', 'IND-050', 'IND-051', 'IND-052'],
                'description': 'Standard format for equipment usage and maintenance logs.'
            },

            # RRS
            {
                'code': 'DOC-RRS-01', 'title': 'Patient Record Policy', 'batch': 'RRS',
                'document_kind': DocumentKind.POLICY, 'evidence_nature': EvidenceNature.ONE_TIME,
                'indicators': ['IND-054', 'IND-055', 'IND-056', 'IND-057', 'IND-058'],
                'description': 'Policy governing the maintenance, retention, and security of patient records.'
            },
            {
                'code': 'DOC-RRS-02', 'title': 'Critical Result Notification SOP/Register', 'batch': 'RRS',
                'document_kind': DocumentKind.REGISTER, 'evidence_nature': EvidenceNature.RECURRING,
                'frequency': RecurrenceFrequency.AS_NEEDED, 'register_entry_needed': True,
                'indicators': ['IND-060'], 'description': 'Protocol and log for reporting critical lab values.'
            },

            # QA
            {
                'code': 'DOC-QA-01', 'title': 'Quality Assurance SOP (IQA & EQA)', 'batch': 'QA',
                'document_kind': DocumentKind.SOP, 'evidence_nature': EvidenceNature.ONE_TIME,
                'staff_awareness_needed': True, 'indicators': ['IND-063', 'IND-064', 'IND-065'],
                'description': 'Comprehensive QA program including internal and external components.'
            },
            {
                'code': 'DOC-QA-02', 'title': 'EQA Participation Record', 'batch': 'QA',
                'document_kind': DocumentKind.REPORT, 'evidence_nature': EvidenceNature.RECURRING,
                'frequency': RecurrenceFrequency.QUARTERLY, 'indicators': ['IND-066', 'IND-067'],
                'description': 'Evidence of participation in External Quality Assurance schemes.'
            },
            {
                'code': 'DOC-QA-03', 'title': 'IQA Control Record', 'batch': 'QA',
                'document_kind': DocumentKind.REGISTER, 'evidence_nature': EvidenceNature.RECURRING,
                'frequency': RecurrenceFrequency.DAILY, 'register_entry_needed': True,
                'indicators': ['IND-074'], 'description': 'Daily monitoring logs for internal quality control.'
            },

            # BSBS
            {
                'code': 'DOC-BSBS-01', 'title': 'Biosafety SOP', 'batch': 'BSBS',
                'document_kind': DocumentKind.SOP, 'evidence_nature': EvidenceNature.ONE_TIME,
                'staff_awareness_needed': True, 'indicators': ['IND-079', 'IND-080'],
                'description': 'Safety guidelines for handling biological materials.'
            },
            {
                'code': 'DOC-BSBS-02', 'title': 'Waste Management SOP', 'batch': 'BSBS',
                'document_kind': DocumentKind.SOP, 'evidence_nature': EvidenceNature.ONE_TIME,
                'staff_awareness_needed': True, 'physical_confirmation_needed': True,
                'indicators': ['IND-092', 'IND-093', 'IND-094', 'IND-095', 'IND-096'],
                'description': 'Policy for segregation, collection, and disposal of laboratory waste.'
            },

            # PATIENT
            {
                'code': 'DOC-PAT-01', 'title': 'Patient Complaint Register', 'batch': 'PATIENT',
                'document_kind': DocumentKind.REGISTER, 'evidence_nature': EvidenceNature.RECURRING,
                'frequency': RecurrenceFrequency.MONTHLY, 'register_entry_needed': True,
                'indicators': ['IND-116', 'IND-117'], 'description': 'Log for recording and tracking patient grievances.'
            },
            {
                'code': 'DOC-PAT-02', 'title': 'Confidentiality Policy', 'batch': 'PATIENT',
                'document_kind': DocumentKind.POLICY, 'evidence_nature': EvidenceNature.ONE_TIME,
                'staff_awareness_needed': True, 'indicators': ['IND-118'],
                'description': 'Policy ensuring the privacy and confidentiality of patient information.'
            },
        ]

        for d in planned_docs:
            doc, created = PlannedEvidenceDocument.objects.update_or_create(
                code=d['code'],
                defaults={
                    'title': d['title'], 'batch': batch_objs[d['batch']], 'document_kind': d['document_kind'],
                    'evidence_nature': d['evidence_nature'], 'frequency': d.get('frequency', RecurrenceFrequency.NONE),
                    'upload_needed': d.get('upload_needed', True),
                    'display_confirmation_needed': d.get('display_confirmation_needed', False),
                    'physical_confirmation_needed': d.get('physical_confirmation_needed', False),
                    'staff_awareness_needed': d.get('staff_awareness_needed', False),
                    'register_entry_needed': d.get('register_entry_needed', False),
                    'description': d.get('description', '')
                }
            )
            
            # Map indicators
            for ind_no in d['indicators']:
                try:
                    ind = Indicator.objects.get(indicator_no=ind_no)
                    doc.indicators.add(ind)
                    # Also map evidence requirements
                    for req in ind.evidence_requirements.all():
                        doc.evidence_requirements.add(req)
                except Indicator.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Indicator {ind_no} not found for doc {doc.code}"))

            if created:
                self.stdout.write(f"Created planned doc: {doc.title}")

        # 3. Create catch-all documents for each batch and map remaining indicators
        self.stdout.write("Mapping remaining indicators...")
        
        # Define a mapping from Functional Area to Batch Code
        fa_to_batch = {
            'ROM': 'GOV',
            'FMS': 'FMS',
            'HRM': 'HRM',
            'MER': 'MER',
            'RRS': 'RRS',
            'QA': 'QA',
            'BSBS': 'BSBS',
            'PRE': 'PATIENT'
        }

        indicators = Indicator.objects.all().prefetch_related('evidence_requirements', 'planned_documents', 'evidence_profile')
        for ind in indicators:
            if ind.planned_documents.exists():
                continue
            
            # Determine batch
            batch_code = fa_to_batch.get(ind.functional_area_code, 'GOV')
            batch = batch_objs[batch_code]
            
            # Create a specific planned doc for this indicator if it looks unique, 
            # or map to a "General" doc for that category.
            
            profile = getattr(ind, 'evidence_profile', None)
            kind = DocumentKind.OTHER
            if profile:
                from core.constants import PrimaryEvidenceType
                if profile.primary_evidence_type == PrimaryEvidenceType.SOP_POLICY:
                    kind = DocumentKind.SOP
                elif profile.primary_evidence_type == PrimaryEvidenceType.REGISTER_LOGBOOK:
                    kind = DocumentKind.REGISTER
                elif profile.primary_evidence_type == PrimaryEvidenceType.DISPLAY_NOTICE:
                    kind = DocumentKind.DISPLAY_NOTICE
            
            doc_title = f"Evidence for {ind.indicator_no}"
            doc_code = f"DOC-AUTO-{ind.indicator_no}"
            
            doc, created = PlannedEvidenceDocument.objects.get_or_create(
                code=doc_code,
                defaults={
                    'title': doc_title, 'batch': batch, 'document_kind': kind,
                    'description': f"Auto-generated planning document for {ind.indicator_no}."
                }
            )
            doc.indicators.add(ind)
            for req in ind.evidence_requirements.all():
                doc.evidence_requirements.add(req)
            
            if created:
                # Sync requirements from profile
                if profile:
                    doc.upload_needed = profile.upload_required
                    doc.register_entry_needed = profile.register_required
                    doc.display_confirmation_needed = profile.display_required
                    doc.physical_confirmation_needed = profile.physical_proof_required
                    doc.staff_awareness_needed = profile.staff_awareness_required
                    doc.save()

        self.stdout.write(self.style.SUCCESS('Seeding and mapping complete.'))
