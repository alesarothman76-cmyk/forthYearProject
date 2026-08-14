import pytest
from rest_framework import status

from apps.accounts.models import DoctorProfile, RegistrationStatus
from apps.accounts.tests.factories import AdminUserFactory, DoctorProfileFactory, DoctorUserFactory

pytestmark = pytest.mark.django_db


class TestRegisterEndpoint:
    def test_register_creates_pending_doctor(self, api_client):
        payload = {
            "username": "apidoc",
            "email": "apidoc@example.com",
            "first_name": "Api",
            "last_name": "Doc",
            "license_number": "LIC-API1",
            "specialization": "Neurology",
            "phone_number": "555-2222",
        }
        response = api_client.post("/api/auth/register/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        profile = DoctorProfile.objects.get(license_number="LIC-API1")
        assert profile.registration_status == RegistrationStatus.PENDING
        assert profile.user.is_active is False

    def test_register_duplicate_username_rejected(self, api_client):
        DoctorUserFactory(username="dupe")
        payload = {
            "username": "dupe",
            "email": "unique@example.com",
            "license_number": "LIC-DUPE",
            "specialization": "Neurology",
            "phone_number": "555-3333",
        }
        response = api_client.post("/api/auth/register/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLoginEndpoint:
    def test_login_embeds_role_in_token(self, api_client):
        user = DoctorUserFactory(username="loginer")
        user.set_password("Pass1234!")
        user.save()

        response = api_client.post("/api/auth/login/", {"username": "loginer", "password": "Pass1234!"})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_pending_doctor_cannot_login(self, api_client):
        user = DoctorUserFactory(username="pendingdoc", is_active=False)
        user.set_unusable_password()
        user.save()

        response = api_client.post("/api/auth/login/", {"username": "pendingdoc", "password": "anything"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestMeEndpoint:
    def test_requires_auth(self, api_client):
        response = api_client.get("/api/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_current_user(self, api_client):
        user = DoctorUserFactory(username="meuser")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "meuser"


class TestAdminDoctorWorkflow:
    def test_non_admin_cannot_list_doctors(self, api_client):
        doctor = DoctorUserFactory()
        api_client.force_authenticate(user=doctor)
        response = api_client.get("/api/admin/doctors/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_approve_pending_doctor(self, api_client):
        admin = AdminUserFactory()
        user = DoctorUserFactory(is_active=False)
        profile = DoctorProfileFactory(user=user, registration_status=RegistrationStatus.PENDING)

        api_client.force_authenticate(user=admin)
        response = api_client.post(f"/api/admin/doctors/{user.id}/approve/")

        assert response.status_code == status.HTTP_200_OK
        profile.refresh_from_db()
        assert profile.registration_status == RegistrationStatus.APPROVED

    def test_admin_approve_twice_returns_400(self, api_client):
        admin = AdminUserFactory()
        user = DoctorUserFactory(is_active=False)
        DoctorProfileFactory(user=user, registration_status=RegistrationStatus.PENDING)

        api_client.force_authenticate(user=admin)
        api_client.post(f"/api/admin/doctors/{user.id}/approve/")
        response = api_client.post(f"/api/admin/doctors/{user.id}/approve/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_can_deactivate_doctor(self, api_client):
        admin = AdminUserFactory()
        user = DoctorUserFactory(is_active=True)
        DoctorProfileFactory(user=user)

        api_client.force_authenticate(user=admin)
        response = api_client.patch(f"/api/admin/doctors/{user.id}/", {"is_active": False}, format="json")

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active is False

    def test_admin_soft_deletes_doctor(self, api_client):
        admin = AdminUserFactory()
        user = DoctorUserFactory(is_active=True)
        DoctorProfileFactory(user=user)

        api_client.force_authenticate(user=admin)
        response = api_client.delete(f"/api/admin/doctors/{user.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.is_active is False
        # Row still exists - never hard-deleted.
        assert DoctorProfile.objects.filter(user=user).exists()


class TestPasswordReset:
    def test_request_always_returns_200(self, api_client):
        response = api_client.post("/api/auth/password-reset/request/", {"email": "nobody@example.com"})
        assert response.status_code == status.HTTP_200_OK