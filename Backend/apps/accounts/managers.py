from django.contrib.auth.models import UserManager


class UserAccountManager(UserManager):
    """
    Ensures `createsuperuser` defaults to role=ADMIN so bootstrapping an
    admin via the CLI works out of the box.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Local import to avoid a circular import between models.py and
        # managers.py at module load time.
        from apps.accounts.models import Role

        extra_fields.setdefault("role", Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)
