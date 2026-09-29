from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()


class AuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in
    with either their username or email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Try to find user by username OR email (case-insensitive)
        try:
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None

        # Check password validity
        if not user.is_active:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
