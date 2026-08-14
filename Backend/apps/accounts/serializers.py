from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import DoctorProfile, RegistrationStatus

User = get_user_model()


class RoleClaimTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Embeds role and username directly in the JWT payload - lets the React
    frontend branch UI (admin vs doctor) without an extra /api/me/
    round-trip immediately after login.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token


class DoctorRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    license_number = serializers.CharField(max_length=64)
    specialization = serializers.CharField(max_length=128)
    phone_number = serializers.CharField(max_length=32)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_license_number(self, value):
        if DoctorProfile.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("A doctor with this license number is already registered.")
        return value


class MeSerializer(serializers.ModelSerializer):
    doctor_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "is_active", "doctor_profile"]

    def get_doctor_profile(self, obj):
        profile = getattr(obj, "doctor_profile", None)
        if profile is None:
            return None
        return {
            "license_number": profile.license_number,
            "specialization": profile.specialization,
            "phone_number": profile.phone_number,
            "registration_status": profile.registration_status,
        }


class DoctorAdminListSerializer(serializers.ModelSerializer):
    """Admin-facing view of a doctor account + registration status."""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    is_active = serializers.BooleanField(source="user.is_active", read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "username",
            "email",
            "is_active",
            "license_number",
            "specialization",
            "phone_number",
            "registration_status",
            "reviewed_at",
            "rejection_reason",
            "created_at",
        ]


class DoctorAdminUpdateSerializer(serializers.Serializer):
    """PATCH /api/admin/doctors/{user_id}/ - only is_active is toggleable here."""

    is_active = serializers.BooleanField()


class RejectDoctorSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=512, required=False, allow_blank=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)
