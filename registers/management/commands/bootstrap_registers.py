from django.core.management.base import BaseCommand
from registers.models import RegisterDefinition

class Command(BaseCommand):
    help = 'Bootstrap default registers'

    def handle(self, *args, **kwargs):
        default_registers = [
            "Temperature Log",
            "Equipment Logbook",
            "Equipment Maintenance Register",
            "Calibration Register",
            "Reagent Inventory",
            "Stock Register",
            "EQA Record",
            "IQA / Process Cycle Record",
            "Complaint Register",
            "Critical Result Register",
            "Fire Drill Register",
            "Training Register",
            "Waste Disposal Register",
            "Incident / Sentinel Event Register"
        ]
        
        created_count = 0
        for name in default_registers:
            reg, created = RegisterDefinition.objects.get_or_create(
                name=name,
                defaults={'category': 'General'}
            )
            if created:
                created_count += 1
                
        # Optional: Auto-link to evidence requirements that look like registers
        # We can do this based on DocumentType.REGISTER or DocumentType.LOGBOOK
        
        self.stdout.write(self.style.SUCCESS(f'Successfully bootstrapped {created_count} default registers.'))
