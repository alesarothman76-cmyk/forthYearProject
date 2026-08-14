from django.urls import path

from apps.mri_analysis import views

urlpatterns = [
    path("mri-scans/", views.MRIScanListCreateView.as_view(), name="mri-scan-list-create"),
    path("mri-scans/<int:pk>/", views.MRIScanDetailView.as_view(), name="mri-scan-detail"),
]
