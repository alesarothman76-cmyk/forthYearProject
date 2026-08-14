from django.db.models import OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsActiveDoctor, IsAdmin
from apps.patients import services
from apps.patients.models import Patient
from apps.patients.serializers import AdminPatientSerializer, PatientSerializer, PatientWriteSerializer


def _search_filter(qs, search_term):
    if not search_term:
        return qs
    return qs.filter(Q(full_name__icontains=search_term) | Q(national_id__icontains=search_term))


def _gender_filter(qs, gender):
    if not gender:
        return qs
    return qs.filter(gender=gender)


def _is_active_filter(qs, is_active_value):
    if is_active_value is None:
        return qs
    return qs.filter(is_active=str(is_active_value).lower() == "true")


def _doctor_filter(qs, doctor_id):
    if not doctor_id:
        return qs
    return qs.filter(created_by_doctor_id=doctor_id)


def _apply_admin_filters(qs, params):
    qs = _search_filter(qs, params.get("search"))
    qs = _is_active_filter(qs, params.get("is_active"))
    qs = _doctor_filter(qs, params.get("doctor_id"))
    return qs


def _status_filter(qs, status_value):
    if not status_value:
        return qs
    from apps.mri_analysis.models import AIAnalysisResult

    latest_analysis = AIAnalysisResult.objects.filter(
        mri_scan__patient=OuterRef("pk")
    ).order_by("-created_at")
    return qs.annotate(
        latest_predicted_class=Subquery(latest_analysis.values("predicted_class")[:1])
    ).filter(latest_predicted_class=status_value)


def _apply_filters(qs, params):
    qs = _search_filter(qs, params.get("search"))
    qs = _gender_filter(qs, params.get("gender"))
    qs = _is_active_filter(qs, params.get("is_active"))
    qs = _status_filter(qs, params.get("status"))
    return qs


class PatientListCreateView(APIView):
    permission_classes = [IsActiveDoctor]

    def get(self, request):
        doctor = request.user.doctor_profile
        qs = Patient.all_objects.filter(created_by_doctor=doctor)
        qs = _apply_filters(qs, request.query_params)
        return Response(PatientSerializer(qs.order_by("-created_at"), many=True).data)

    def post(self, request):
        serializer = PatientWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = services.create_patient(doctor=request.user.doctor_profile, **serializer.validated_data)
        return Response(PatientSerializer(patient).data, status=status.HTTP_201_CREATED)


class PatientDetailView(APIView):
    permission_classes = [IsActiveDoctor]

    def get_object(self, request, pk):
        # Queryset filtered to the requester's own records BEFORE lookup -
        # a non-owned object returns 404, not 403 (avoids leaking existence).
        doctor = request.user.doctor_profile
        return get_object_or_404(Patient, pk=pk, created_by_doctor=doctor)

    def get(self, request, pk):
        patient = self.get_object(request, pk)
        return Response(PatientSerializer(patient).data)

    def patch(self, request, pk):
        patient = self.get_object(request, pk)
        serializer = PatientWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = services.update_patient(patient=patient, **serializer.validated_data)
        return Response(PatientSerializer(patient).data)

    def delete(self, request, pk):
        patient = self.get_object(request, pk)
        services.archive_patient(patient=patient)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminPatientListView(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminPatientSerializer
    

    def get_queryset(self):
        qs = Patient.all_objects.select_related("created_by_doctor__user").all()
        return _apply_admin_filters(qs, self.request.query_params).order_by("-created_at")


class AdminPatientDetailView(RetrieveAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminPatientSerializer
    queryset = Patient.all_objects.select_related("created_by_doctor__user").all()
    # No create/update/delete verbs exist here at all - architecturally
    # absent (RetrieveAPIView only implements GET), not permission-blocked.


class PatientHistoryView(APIView):
    """
    Phase 5 - Results/History. Aggregates a patient's full scan history in
    one view: every MRI scan the owning doctor uploaded for this patient,
    each with its nested AI analysis result (if any) and the reports
    written against it. A single round-trip instead of the frontend
    stitching together /mri-scans/?patient= and /reports/?patient= itself.
    """

    permission_classes = [IsActiveDoctor]

    def get(self, request, pk):
        # Local imports - avoids a module-level import cycle between
        # patients/views.py and mri_analysis/reports (which themselves
        # import from patients.models).
        from apps.mri_analysis.serializers import MRIScanSerializer
        from apps.reports.serializers import ReportSerializer

        doctor = request.user.doctor_profile
        patient = get_object_or_404(Patient, pk=pk, created_by_doctor=doctor)

        scans = (
            patient.mri_scans.filter(uploaded_by_doctor=doctor)
            .select_related("analysis_result")
            .prefetch_related("reports")
            .order_by("-created_at")
        )

        scan_history = []
        for scan in scans:
            scan_data = MRIScanSerializer(scan).data
            scan_data["reports"] = ReportSerializer(scan.reports.all().order_by("-created_at"), many=True).data
            scan_history.append(scan_data)

        return Response(
            {
                "patient": PatientSerializer(patient).data,
                "scans": scan_history,
            }
        )
