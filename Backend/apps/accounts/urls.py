from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("auth/register/", views.RegisterDoctorView.as_view(), name="auth-register"),
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", views.RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("auth/password-reset/request/", views.PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("auth/password-reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("me/", views.MeView.as_view(), name="me"),
    path("admin/doctors/", views.AdminDoctorListView.as_view(), name="admin-doctor-list"),
    path("admin/doctors/<int:pk>/", views.AdminDoctorDetailView.as_view(), name="admin-doctor-detail"),
    path("admin/doctors/<int:pk>/approve/", views.AdminDoctorApproveView.as_view(), name="admin-doctor-approve"),
    path("admin/doctors/<int:pk>/reject/", views.AdminDoctorRejectView.as_view(), name="admin-doctor-reject"),
]
