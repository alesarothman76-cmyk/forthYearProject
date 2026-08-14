from rest_framework import serializers

from apps.mri_analysis.models import AIAnalysisResult, MRIScan


class AIAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisResult
        fields = [
            "predicted_class",
            "confidence_score",
            "class_probabilities",
            "model_version",
            "execution_time_seconds",
            "heatmap_image",
        ]


class MRIScanSerializer(serializers.ModelSerializer):
    # Nested automatically into the MRIScan API response.
    analysis_result = AIAnalysisResultSerializer(read_only=True)

    class Meta:
        model = MRIScan
        fields = [
            "id",
            "patient",
            "uploaded_by_doctor",
            "original_file",
            "processed_image",
            "dicom_metadata",
            "status",
            "error_message",
            "analysis_result",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uploaded_by_doctor",
            "processed_image",
            "dicom_metadata",
            "status",
            "error_message",
            "created_at",
            "updated_at",
        ]


class MRIScanUploadSerializer(serializers.Serializer):
    patient = serializers.IntegerField()
    file = serializers.FileField()
