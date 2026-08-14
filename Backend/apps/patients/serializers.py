from rest_framework import serializers

from apps.patients.models import Gender, Patient


class PatientSerializer(serializers.ModelSerializer):
    """Doctor-facing: full record, including medical_history."""

    class Meta:
        model = Patient
        fields = [
            "id",
            "national_id",
            "full_name",
            "date_of_birth",
            "gender",
            "medical_history",
            "email",
            "created_by_doctor",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by_doctor", "is_active", "created_at", "updated_at"]


class PatientWriteSerializer(serializers.Serializer):
    """
    Used for both create and update. national_id and created_by_doctor are
    intentionally absent from update use - the service layer strips them
    even if a caller sneaks them into the payload (see services.py).
    """

    national_id = serializers.CharField(max_length=64, required=False)
    full_name = serializers.CharField(max_length=255, required=False)
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=Gender.choices, required=False)
    medical_history = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class AdminPatientSerializer(serializers.ModelSerializer):
    """
    Structurally excludes medical_history - the field literally isn't in
    this serializer, so no future refactor can accidentally leak it through
    this endpoint.
    """

    created_by_doctor_name = serializers.SerializerMethodField()
    created_by_doctor_username = serializers.CharField(source="created_by_doctor.user.username", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "national_id",
            "full_name",
            "date_of_birth",
            "gender",
            "email",
            "created_by_doctor_name",
            "created_by_doctor_username",
            "is_active",
            "created_at",
        ]

    def get_created_by_doctor_name(self, obj):
        user = obj.created_by_doctor.user
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or user.username
