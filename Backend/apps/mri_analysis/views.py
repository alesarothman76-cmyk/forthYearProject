from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsActiveDoctor
from apps.mri_analysis import services
from apps.mri_analysis.models import MRIScan
from apps.mri_analysis.serializers import MRIScanSerializer, MRIScanUploadSerializer
from apps.patients.models import Patient


class MRIScanListCreateView(APIView):
    permission_classes = [IsActiveDoctor]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        doctor = request.user.doctor_profile
        qs = MRIScan.objects.filter(uploaded_by_doctor=doctor)
        patient_id = request.query_params.get("patient")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return Response(MRIScanSerializer(qs.order_by("-created_at"), many=True).data)

    def post(self, request):
        serializer = MRIScanUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = request.user.doctor_profile
        # Doctor-owns-patient enforced using the same 404-not-403 pattern as
        # Patients - uploading a scan for a patient you don't own is rejected.
        patient = get_object_or_404(Patient, pk=serializer.validated_data["patient"], created_by_doctor=doctor)

        scan = services.upload_and_process_scan(
            doctor=doctor,
            patient=patient,
            uploaded_file=serializer.validated_data["file"],
        )
        return Response(MRIScanSerializer(scan).data, status=status.HTTP_201_CREATED)


class MRIScanDetailView(APIView):
    permission_classes = [IsActiveDoctor]

    def get(self, request, pk):
        doctor = request.user.doctor_profile
        scan = get_object_or_404(MRIScan, pk=pk, uploaded_by_doctor=doctor)
        return Response(MRIScanSerializer(scan).data)
