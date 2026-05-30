import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Bootstrap admin user'

    def handle(self, *args, **kwargs):
        admin_user = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_pass = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')
        admin_email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        
        if not User.objects.filter(username=admin_user).exists():
            User.objects.create_superuser(username=admin_user, email=admin_email, password=admin_pass)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {admin_user}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser {admin_user} already exists.'))
