import pytest
from django.utils import timezone

from apps.accounts.models import PasswordResetCode, RegistrationStatus
from apps.accounts.tests.factories import DoctorProfileFactory, DoctorUserFactory

pytestmark = pytest.mark.django_db


class TestUser:
    def test_createsuperuser_defaults_to_admin_role(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        admin = User.objects.create_superuser(username="root", email="root@example.com", password="x")
        assert admin.role == "ADMIN"


class TestDoctorProfile:
    def test_default_registration_status_is_pending(self):
        user = DoctorUserFactory(is_active=False)
        profile = DoctorProfileFactory(user=user, registration_status=RegistrationStatus.PENDING)
        assert profile.registration_status == RegistrationStatus.PENDING


class TestPasswordResetCode:
    def test_generate_for_user_invalidates_previous_codes(self):
        user = DoctorUserFactory()
        first = PasswordResetCode.generate_for_user(user)
        second = PasswordResetCode.generate_for_user(user)

        first.refresh_from_db()
        assert first.is_used is True
        assert second.is_used is False
        assert len(second.code) == 6

    def test_is_valid_false_when_used(self):
        user = DoctorUserFactory()
        code = PasswordResetCode.generate_for_user(user)
        code.is_used = True
        code.save()
        assert code.is_valid() is False

    def test_is_valid_false_when_expired(self):
        user = DoctorUserFactory()
        code = PasswordResetCode.generate_for_user(user)
        code.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        code.save()
        assert code.is_valid() is False
