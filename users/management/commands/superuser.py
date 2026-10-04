
from django.core.management.base import BaseCommand
from users.services import SuperUser


class Command(BaseCommand):
    help = "Create default superuser"

    def handle(self, *args, **kwargs):
        user = SuperUser()
        if not user.exists():
            user.create()
            self.stdout.write(self.style.SUCCESS("Super user created successfully"))
       