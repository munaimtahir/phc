from django.core.management.base import BaseCommand
from indicators.models import Indicator
from evidence.models import IndicatorEvidenceProfile

class Command(BaseCommand):
    help = 'Audits the IndicatorEvidenceProfile data for completeness and confidence.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Evidence Profile Audit Report ---'))

        total_indicators = Indicator.objects.count()
        profiles = IndicatorEvidenceProfile.objects.all()
        total_profiles = profiles.count()

        self.stdout.write(f"Total Indicators: {total_indicators}")
        self.stdout.write(f"Indicators with Profiles: {total_profiles}")
        
        missing_profiles = total_indicators - total_profiles
        if missing_profiles > 0:
            self.stdout.write(self.style.WARNING(f"Indicators MISSING Profiles: {missing_profiles}"))
        else:
            self.stdout.write(self.style.SUCCESS("All indicators have a profile."))

        self.stdout.write("\n--- Profile Confidence ---")
        low_confidence = profiles.filter(profile_confidence='LOW').count()
        medium_confidence = profiles.filter(profile_confidence='MEDIUM').count()
        high_confidence = profiles.filter(profile_confidence='HIGH').count()
        self.stdout.write(f"High Confidence: {high_confidence}")
        self.stdout.write(f"Medium Confidence: {medium_confidence}")
        self.stdout.write(f"Low Confidence: {low_confidence}")

        self.stdout.write("\n--- Requirement Type Summary ---")
        upload_required = profiles.filter(upload_required=True).count()
        register_required = profiles.filter(register_required=True).count()
        physical_proof_required = profiles.filter(physical_proof_required=True).count()
        display_required = profiles.filter(display_required=True).count()
        staff_awareness_required = profiles.filter(staff_awareness_required=True).count()
        recurring_required = profiles.filter(recurring_required=True).count()

        self.stdout.write(f"Upload Required: {upload_required}")
        self.stdout.write(f"Register/Logbook Required: {register_required}")
        self.stdout.write(f"Physical Proof Required: {physical_proof_required}")
        self.stdout.write(f"Display Required: {display_required}")
        self.stdout.write(f"Staff Awareness Required: {staff_awareness_required}")
        self.stdout.write(f"Recurring Evidence Required: {recurring_required}")
        
        self.stdout.write(self.style.SUCCESS('\n--- Audit Complete ---'))
