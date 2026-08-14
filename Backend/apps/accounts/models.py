import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.accounts.managers import UserAccountManager
from apps.common.models import TimeStampedModel


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    DOCTOR = "DOCTOR", "Doctor"


class User(AbstractUser):
    """
    Custom user, AUTH_USER_MODEL. Set before first migration - cannot be
    changed later without a full DB reset.
    """

    role = models.CharField(max_length=10, choices=Role.choices)

    objects = UserAccountManager()

    def __str__(self):
        return self.username


class RegistrationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class DoctorProfile(TimeStampedModel):
    """1:1 with User."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    license_number = models.CharField(max_length=64, unique=True)
    specialization = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=32)

    registration_status = models.CharField(
        max_length=10, choices=RegistrationStatus.choices, default=RegistrationStatus.PENDING
    )
    reviewed_by_admin = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="doctors_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=512, blank=True)

    # NOTE: an earlier version of this model had `created_by_admin` (from
    # when admin created doctors directly). That field was REMOVED when the
    # design changed to self-registration (see Section 4.2 of the
    # implementation summary). Do not re-add it.

    def __str__(self):
        return f"Dr. {self.user.username} ({self.registration_status})"


class PasswordResetCode(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_codes")
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_for_user(cls, user):
        """Invalidates any previous unused codes for this user, then creates a fresh one."""
        from django.conf import settings

        cls.objects.filter(user=user, is_used=False).update(is_used=True)

        code = "".join(secrets.choice("0123456789") for _ in range(6))
        ttl_minutes = settings.PASSWORD_RESET_CODE_TTL_MINUTES
        expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)

        return cls.objects.create(user=user, code=code, expires_at=expires_at)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"ResetCode(user={self.user_id}, used={self.is_used})"
