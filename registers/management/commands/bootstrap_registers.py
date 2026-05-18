from django.core.management.base import BaseCommand
from registers.models import RegisterDefinition

class Command(BaseCommand):
    help = 'Bootstraps the 14 default digital registers for PHC'

    def handle(self, *args, **options):
        default_registers = [
            {"name": "Temperature Log", "category": "Environmental", "frequency": "Daily"},
            {"name": "Equipment Logbook", "category": "Equipment", "frequency": "Event-based"},
            {"name": "Equipment Maintenance Register", "category": "Equipment", "frequency": "Event-based"},
            {"name": "Calibration Register", "category": "Equipment", "frequency": "Event-based"},
            {"name": "Reagent Inventory", "category": "Inventory", "frequency": "Weekly"},
            {"name": "Stock Register", "category": "Inventory", "frequency": "Weekly"},
            {"name": "EQA Record", "category": "Quality", "frequency": "Monthly"},
            {"name": "IQA / Process Cycle Record", "category": "Quality", "frequency": "Daily"},
            {"name": "Complaint Register", "category": "Management", "frequency": "Event-based"},
            {"name": "Critical Result Register", "category": "Clinical", "frequency": "Event-based"},
            {"name": "Fire Drill Register", "category": "Safety", "frequency": "Annual"},
            {"name": "Training Register", "category": "HR", "frequency": "Event-based"},
            {"name": "Waste Disposal Register", "category": "Safety", "frequency": "Daily"},
            {"name": "Incident / Sentinel Event Register", "category": "Management", "frequency": "Event-based"},
        ]
        
        count = 0
        for reg in default_registers:
            obj, created = RegisterDefinition.objects.get_or_create(
                name=reg["name"],
                defaults={
                    "category": reg["category"],
                    "frequency": reg["frequency"],
                }
            )
            if created:
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully bootstrapped {count} new registers.'))
