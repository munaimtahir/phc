from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from indicators.models import Indicator
from evidence.models import IndicatorEvidenceProfile
from registers.models import RegisterDefinition
from core.constants import PrimaryEvidenceType, RecurrenceFrequency, ProfileConfidence, ProfileSource

class Command(BaseCommand):
    help = 'Seed evidence profiles for all indicators based on deterministic rules.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing profiles instead of skipping them.',
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed evidence profiles...'))
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        indicators = Indicator.objects.all()
        if not indicators.exists():
            raise CommandError("No indicators found. Please run 'import_phc_indicators' first.")

        for indicator in indicators:
            profile_exists = hasattr(indicator, 'evidence_profile')
            
            if profile_exists and not kwargs['update']:
                skipped_count += 1
                continue

            # 1. Apply deterministic classification rules
            profile_data = self.classify_indicator(indicator)

            # 2. Apply manual high-value overrides
            override_data = self.get_manual_overrides(indicator)
            profile_data.update(override_data)
            
            if profile_exists:
                profile = indicator.evidence_profile
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()
                updated_count += 1
            else:
                IndicatorEvidenceProfile.objects.create(indicator=indicator, **profile_data)
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeding complete. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}'
        ))

    def classify_indicator(self, indicator):
        text = f"{indicator.indicator_text} {indicator.compliance_requirement or ''}".lower()
        
        # Default data
        data = {
            'primary_evidence_type': PrimaryEvidenceType.OTHER,
            'upload_required': True,
            'profile_confidence': ProfileConfidence.LOW,
            'user_action_prompt': 'Upload the required evidence document(s) and add remarks.'
        }

        if 'sop' in text or 'policy' in text or 'procedure' in text:
            data.update({
                'primary_evidence_type': PrimaryEvidenceType.SOP_POLICY,
                'approval_required': True,
                'staff_awareness_required': True,
                'user_action_prompt': 'Upload the approved SOP/policy and provide evidence of staff awareness.',
                'profile_confidence': ProfileConfidence.MEDIUM,
            })

        if 'register' in text or 'log' in text or 'record' in text:
            data.update({
                'primary_evidence_type': PrimaryEvidenceType.REGISTER_LOGBOOK,
                'register_required': True,
                'recurring_required': True,
                'recurrence_frequency': RecurrenceFrequency.AS_NEEDED,
                'user_action_prompt': 'Add entries to the relevant register/logbook.',
                'profile_confidence': ProfileConfidence.MEDIUM,
            })
            # Try to link register
            if 'complaint' in text:
                data['suggested_register'] = RegisterDefinition.objects.filter(name__icontains='Complaint').first()
            elif 'equipment' in text:
                data['suggested_register'] = RegisterDefinition.objects.filter(name__icontains='Equipment').first()

        if 'display' in text or 'sign board' in text:
            data.update({
                'primary_evidence_type': PrimaryEvidenceType.DISPLAY_NOTICE,
                'display_required': True,
                'physical_proof_required': True,
                'user_action_prompt': 'Upload a photo of the displayed item and confirm its location.',
                'profile_confidence': ProfileConfidence.HIGH,
            })
            
        if 'license' in text or 'registration' in text or 'certificate' in text:
             data.update({
                'primary_evidence_type': PrimaryEvidenceType.LICENSE_CERTIFICATE,
                'upload_required': True,
                'profile_confidence': ProfileConfidence.HIGH,
            })
        
        data['profile_source'] = ProfileSource.SEEDED_FROM_RULES
        return data

    def get_manual_overrides(self, indicator):
        overrides = {
            'IND-007': {
                'primary_evidence_type': PrimaryEvidenceType.DISPLAY_NOTICE,
                'upload_required': True, 'display_required': True, 'physical_proof_required': True, 'approval_required': True,
                'recurring_required': False,
                'display_location': 'Reception / patient waiting area / staff area',
                'user_action_prompt': 'Upload the approved mission statement and confirm that it is displayed for staff and patients.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-011': {
                'primary_evidence_type': PrimaryEvidenceType.DISPLAY_NOTICE,
                'upload_required': True, 'display_required': True, 'physical_proof_required': True, 'approval_required': True,
                'recurring_required': False,
                'display_location': 'Reception / staff area',
                'user_action_prompt': 'Upload the approved organogram and confirm it is displayed.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-023': {
                'primary_evidence_type': PrimaryEvidenceType.REPORT_AUDIT,
                'upload_required': True, 'register_required': True, 'recurring_required': True,
                'recurrence_frequency': RecurrenceFrequency.ANNUAL,
                'user_action_prompt': 'Upload or enter the latest annual mock drill record with observations and corrective actions.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-049': {
                'primary_evidence_type': PrimaryEvidenceType.REGISTER_LOGBOOK,
                'register_required': True, 'recurring_required': True, 'recurrence_frequency': RecurrenceFrequency.AS_NEEDED,
                'user_action_prompt': 'Add equipment logbook entries or upload scanned logbook pages for each equipment.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-060': {
                'primary_evidence_type': PrimaryEvidenceType.REGISTER_LOGBOOK,
                'upload_required': True, 'register_required': True, 'recurring_required': True, 'staff_awareness_required': True,
                'recurrence_frequency': RecurrenceFrequency.AS_NEEDED,
                'user_action_prompt': 'Maintain critical result/notifiable disease reporting register and upload the approved list/procedure.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-063': {
                'primary_evidence_type': PrimaryEvidenceType.SOP_POLICY,
                'upload_required': True, 'staff_awareness_required': True, 'approval_required': True,
                'readiness_rule': 'Ready only if QA SOP uploaded, approved, and covers both IQA and EQA components, with staff communication evidence.',
                'user_action_prompt': 'Upload approved QA SOP covering both IQA and EQA and attach staff communication/training evidence.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-074': {
                'primary_evidence_type': PrimaryEvidenceType.REGISTER_LOGBOOK,
                'upload_required': True, 'register_required': True, 'recurring_required': True,
                'recurrence_frequency': RecurrenceFrequency.AS_NEEDED,
                'user_action_prompt': 'Enter or upload IQA control records showing availability and use of controls.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-092': {
                'primary_evidence_type': PrimaryEvidenceType.SOP_POLICY,
                'upload_required': True, 'staff_awareness_required': True, 'approval_required': True, 'physical_proof_required': True,
                'user_action_prompt': 'Upload waste management SOP and confirm required waste segregation/handling arrangements.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-116': {
                'primary_evidence_type': PrimaryEvidenceType.REGISTER_LOGBOOK,
                'register_required': True, 'recurring_required': True, 'recurrence_frequency': RecurrenceFrequency.MONTHLY,
                'user_action_prompt': 'Maintain complaint register. If no complaint occurred, record monthly no-complaint review.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            },
            'IND-118': {
                'primary_evidence_type': PrimaryEvidenceType.SOP_POLICY,
                'upload_required': True, 'staff_awareness_required': True, 'approval_required': True,
                'user_action_prompt': 'Upload confidentiality policy/SOP and attach staff awareness or confidentiality undertaking evidence.',
                'profile_confidence': ProfileConfidence.HIGH, 'profile_source': ProfileSource.MANUAL_REVIEWED,
            }
        }
        
        # Also try to link registers by name
        if 'suggested_register' not in overrides.get(indicator.indicator_no, {}):
             if 'complaint' in indicator.indicator_text.lower():
                 overrides.setdefault(indicator.indicator_no, {})['suggested_register'] = RegisterDefinition.objects.filter(name__icontains='Complaint').first()

        return overrides.get(indicator.indicator_no, {})
