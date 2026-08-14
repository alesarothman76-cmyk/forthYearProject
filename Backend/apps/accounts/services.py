from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import DoctorProfile, PasswordResetCode, RegistrationStatus, Role

User = get_user_model()


class RegistrationError(Exception):
    pass


@transaction.atomic
def register_doctor(*, username, email, first_name, last_name, license_number, specialization, phone_number):
    """
    Doctor self-registration. Both User and DoctorProfile are created
    atomically - a User with role=DOCTOR must never exist without its
    DoctorProfile.
    """
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=Role.DOCTOR,
        is_active=False,
    )
    user.set_unusable_password()
    user.save()

    profile = DoctorProfile.objects.create(
        user=user,
        license_number=license_number,
        specialization=specialization,
        phone_number=phone_number,
        registration_status=RegistrationStatus.PENDING,
    )

    send_mail(
        subject="Registration received",
        message="Your doctor registration has been received and is pending admin approval.",
        from_email=None,
        recipient_list=[user.email],
        fail_silently=True,
    )

    return profile


def approve_doctor(*, profile: DoctorProfile, admin_user):
    if profile.registration_status != RegistrationStatus.PENDING:
        raise RegistrationError("Only a PENDING registration can be approved.")

    with transaction.atomic():
        profile.registration_status = RegistrationStatus.APPROVED
        profile.reviewed_by_admin = admin_user
        profile.reviewed_at = timezone.now()
        profile.save(update_fields=["registration_status", "reviewed_by_admin", "reviewed_at", "updated_at"])

        profile.user.is_active = True
        profile.user.save(update_fields=["is_active"])

        # Reuses the SAME request_password_reset() mechanism as an ordinary
        # "forgot password" flow - no separate "set initial password" path.
        request_password_reset(email=profile.user.email)

    return profile


def reject_doctor(*, profile: DoctorProfile, admin_user, reason=""):
    if profile.registration_status != RegistrationStatus.PENDING:
        raise RegistrationError("Only a PENDING registration can be rejected.")

    profile.registration_status = RegistrationStatus.REJECTED
    profile.reviewed_by_admin = admin_user
    profile.reviewed_at = timezone.now()
    profile.rejection_reason = reason
    profile.save(
        update_fields=["registration_status", "reviewed_by_admin", "reviewed_at", "rejection_reason", "updated_at"]
    )

    send_mail(
        subject="Registration update",
        message=f"Your doctor registration was not approved. Reason: {reason or 'not specified'}",
        from_email=None,
        recipient_list=[profile.user.email],
        fail_silently=True,
    )

    return profile


def set_doctor_active(*, profile: DoctorProfile, is_active: bool):
    profile.user.is_active = is_active
    profile.user.save(update_fields=["is_active"])
    return profile


def soft_delete_doctor(*, profile: DoctorProfile):
    """Soft-delete: sets is_active=False permanently. Same mechanism as deactivate."""
    return set_doctor_active(profile=profile, is_active=False)


def request_password_reset(*, email):
    """
    Always succeeds from the caller's perspective (silent about account
    existence). Silently no-ops (sends no email) if the matched user is
    inactive - a PENDING/REJECTED doctor's email cannot be used to fish for
    a reset code before they're approved.
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    if not user.is_active:
        return

    reset_code = PasswordResetCode.generate_for_user(user)

    send_mail(
        subject="Your password reset code",
        message=f"Your password reset code is: {reset_code.code}",
        from_email=None,
        recipient_list=[user.email],
        fail_silently=True,
    )


class PasswordResetError(Exception):
    pass


@transaction.atomic
def confirm_password_reset(*, email, code, new_password):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise PasswordResetError("Invalid code.")

    reset_code = (
        PasswordResetCode.objects.filter(user=user, code=code, is_used=False).order_by("-created_at").first()
    )
    if reset_code is None or not reset_code.is_valid():
        raise PasswordResetError("Invalid or expired code.")

    user.set_password(new_password)
    user.save(update_fields=["password"])

    reset_code.is_used = True
    reset_code.save(update_fields=["is_used", "updated_at"])
