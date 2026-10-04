from django.conf import settings
from allauth.account.models import EmailAddress
from .models import User


class SuperUser:

    def __init__(self) -> None:
        self.name = "Super User"
        self.email = getattr(settings, "SUPERUSER_EMAIL")
        self.password = getattr(settings, "SUPERUSER_PASSWORD")

    def exists(self):
        return User.objects.filter(email=self.email).exists()

    def create(self):
        if not self.exists():
            user = User()
            user.email = self.email
            user.name = self.name
            user.set_password(self.password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            email = EmailAddress(user=user, email=user.email, primary=True, verified=True)
            email.save()
