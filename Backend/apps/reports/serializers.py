from rest_framework import serializers

from apps.reports.models import Report


class ReportSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="mri_scan.patient_id", read_only=True)
    patient_name = serializers.CharField(source="mri_scan.patient.full_name", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "mri_scan",
            "patient_id",
            "patient_name",
            "created_by_doctor",
            "notes",
            "status",
            "generated_pdf",
            "finalized_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "created_by_doctor",
            "status",
            "generated_pdf",
            "finalized_at",
            "created_at",
            "updated_at",
        ]


class ReportCreateSerializer(serializers.Serializer):
    mri_scan = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)


class ReportUpdateSerializer(serializers.Serializer):
    notes = serializers.CharField(allow_blank=True)
