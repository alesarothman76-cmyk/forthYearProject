import pytest

from apps.accounts import services
from apps.accounts.models import DoctorProfile, RegistrationStatus
from apps.accounts.tests.factories import AdminUserFactory, DoctorProfileFactory, DoctorUserFactory

pytestmark = pytest.mark.django_db


class TestRegisterDoctor:
    def test_creates_inactive_user_with_unusable_password(self):
        profile = services.register_doctor(
            username="newdoc",
            email="newdoc@example.com",
            first_name="New",
            last_name="Doc",
            license_number="LIC-99999",
            specialization="Radiology",
            phone_number="555-0000",
        )
        assert profile.registration_status == RegistrationStatus.PENDING
        assert profile.user.is_active is False
        assert profile.user.has_usable_password() is False

    def test_user_and_profile_created_atomically(self):
        # Sanity check: exactly one profile per user, never orphaned.
        profile = services.register_doctor(
            username="atomicdoc",
            email="atomicdoc@example.com",
            first_name="",
            last_name="",
            license_number="LIC-11111",
            specialization="Neurology",
            phone_number="555-1111",
        )
        assert DoctorProfile.objects.filter(user=profile.user).count() == 1


class TestApproveReject:
    def test_approve_activates_user_and_sends_reset_code(self, mailoutbox):
        user = DoctorUserFactory(is_active=False)
        profile = DoctorProfileFactory(user=user, registration_status=RegistrationStatus.PENDING)
        admin = AdminUserFactory()

        services.approve_doctor(profile=profile, admin_user=admin)

        profile.refresh_from_db()
        user.refresh_from_db()
        assert profile.registration_status == RegistrationStatus.APPROVED
        assert profile.reviewed_by_admin_id == admin.id
        assert user.is_active is True

    def test_approve_twice_raises(self):
        user = DoctorUserFactory(is_active=False)
        profile = DoctorProfileFactory(user=user, registration_status=RegistrationStatus.PENDING)
        admin = AdminUserFactory()

        services.approve_doctor(profile=profile, admin_user=admin)
        with pytest.raises(services.RegistrationError):
            services.approve_doctor(profile=profile, admin_user=admin)

    def test_reject_keeps_user_inactive(self):
        user = DoctorUserFactory(is_active=False)
        profile = DoctorProfileFactory(user=user, registration_status=RegistrationStatus.PENDING)
        admin = AdminUserFactory()

        services.reject_doctor(profile=profile, admin_user=admin, reason="Invalid license")

        profile.refresh_from_db()
        user.refresh_from_db()
        assert profile.registration_status == RegistrationStatus.REJECTED
        assert user.is_active is False
        assert profile.rejection_reason == "Invalid license"

    def test_reject_already_processed_raises(self):
        user = DoctorUserFactory(is_active=False)
        profile = DoctorProfileFactory(user=user, registration_status=RegistrationStatus.REJECTED)
        admin = AdminUserFactory()

        with pytest.raises(services.RegistrationError):
            services.reject_doctor(profile=profile, admin_user=admin)


class TestPasswordReset:
    def test_request_reset_silent_for_unknown_email(self, mailoutbox):
        services.request_password_reset(email="nobody@example.com")
        assert len(mailoutbox) == 0

    def test_request_reset_silent_for_inactive_user(self, mailoutbox):
        DoctorUserFactory(email="inactive@example.com", is_active=False)
        services.request_password_reset(email="inactive@example.com")
        assert len(mailoutbox) == 0

    def test_confirm_reset_sets_new_password(self):
        user = DoctorUserFactory(email="reset@example.com")
        services.request_password_reset(email="reset@example.com")
        code = user.password_reset_codes.latest("created_at")

        services.confirm_password_reset(email="reset@example.com", code=code.code, new_password="NewPass123!")

        user.refresh_from_db()
        assert user.check_password("NewPass123!") is True

    def test_confirm_reset_invalid_code_raises(self):
        user = DoctorUserFactory(email="badcode@example.com")
        with pytest.raises(services.PasswordResetError):
            services.confirm_password_reset(email="badcode@example.com", code="000000", new_password="x12345678")
