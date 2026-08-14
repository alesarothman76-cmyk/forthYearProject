from django.urls import path

from apps.reports import views

urlpatterns = [
    path("reports/", views.ReportListCreateView.as_view(), name="report-list-create"),
    path("reports/<int:pk>/", views.ReportDetailView.as_view(), name="report-detail"),
    path("reports/<int:pk>/finalize/", views.ReportFinalizeView.as_view(), name="report-finalize"),
    path("reports/<int:pk>/pdf/", views.ReportPDFDownloadView.as_view(), name="report-pdf"),
]
