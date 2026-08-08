import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed the single shared-login user for the lab's 2-3 staff (decision #4)."

    def handle(self, *args, **options):
        username = os.environ.get("SHARED_LOGIN_USERNAME", "alshifa")
        password = os.environ.get("SHARED_LOGIN_PASSWORD", "AlShifa#2026")

        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} shared login user '{username}'."))
