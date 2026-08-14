from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsActiveDoctor
from apps.mri_analysis.models import MRIScan
from apps.reports import services
from apps.reports.models import Report, ReportStatus
from apps.reports.serializers import ReportCreateSerializer, ReportSerializer, ReportUpdateSerializer


class ReportListCreateView(APIView):
    permission_classes = [IsActiveDoctor]

    def get(self, request):
        doctor = request.user.doctor_profile
        qs = Report.objects.filter(created_by_doctor=doctor)
        patient_id = request.query_params.get("patient")
        if patient_id:
            qs = qs.filter(mri_scan__patient_id=patient_id)
        scan_id = request.query_params.get("mri_scan")
        if scan_id:
            qs = qs.filter(mri_scan_id=scan_id)
        return Response(ReportSerializer(qs.order_by("-created_at"), many=True).data)

    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doctor = request.user.doctor_profile
        # Same 404-not-403 ownership pattern as Patients/MRI Scans - a scan
        # you don't own can't be reported on.
        scan = get_object_or_404(MRIScan, pk=serializer.validated_data["mri_scan"], uploaded_by_doctor=doctor)

        report = services.create_report(doctor=doctor, mri_scan=scan, notes=serializer.validated_data.get("notes", ""))
        return Response(ReportSerializer(report).data, status=status.HTTP_201_CREATED)


class ReportDetailView(APIView):
    permission_classes = [IsActiveDoctor]

    def get_object(self, request, pk):
        doctor = request.user.doctor_profile
        return get_object_or_404(Report, pk=pk, created_by_doctor=doctor)

    def get(self, request, pk):
        report = self.get_object(request, pk)
        return Response(ReportSerializer(report).data)

    def patch(self, request, pk):
        report = self.get_object(request, pk)
        serializer = ReportUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            report = services.update_report_notes(report=report, notes=serializer.validated_data["notes"])
        except services.ReportError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ReportSerializer(report).data)

    def delete(self, request, pk):
        report = self.get_object(request, pk)
        try:
            services.archive_report(report=report)
        except services.ReportError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReportFinalizeView(APIView):
    permission_classes = [IsActiveDoctor]

    def post(self, request, pk):
        doctor = request.user.doctor_profile
        report = get_object_or_404(Report, pk=pk, created_by_doctor=doctor)
        try:
            report = services.finalize_report(report=report)
        except services.ReportError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ReportSerializer(report).data)


class ReportPDFDownloadView(APIView):
    permission_classes = [IsActiveDoctor]

    def get(self, request, pk):
        doctor = request.user.doctor_profile
        report = get_object_or_404(Report, pk=pk, created_by_doctor=doctor)
        if report.status != ReportStatus.FINALIZED or not report.generated_pdf:
            return Response(
                {"detail": "This report has not been finalized yet - no PDF is available."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return FileResponse(
            report.generated_pdf.open("rb"),
            as_attachment=True,
            filename=f"report_{report.id}.pdf",
            content_type="application/pdf",
        )
