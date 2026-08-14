from django.urls import path

from apps.patients import views

urlpatterns = [
    path("patients/", views.PatientListCreateView.as_view(), name="patient-list-create"),
    path("patients/<int:pk>/", views.PatientDetailView.as_view(), name="patient-detail"),
    path("patients/<int:pk>/history/", views.PatientHistoryView.as_view(), name="patient-history"),
    path("admin/patients/", views.AdminPatientListView.as_view(), name="admin-patient-list"),
    path("admin/patients/<int:pk>/", views.AdminPatientDetailView.as_view(), name="admin-patient-detail"),
]
