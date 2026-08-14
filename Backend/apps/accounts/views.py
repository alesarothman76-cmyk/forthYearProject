from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts import services
from apps.accounts.models import DoctorProfile, RegistrationStatus
from apps.accounts.serializers import (
    DoctorAdminListSerializer,
    DoctorAdminUpdateSerializer,
    DoctorRegistrationSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RejectDoctorSerializer,
    RoleClaimTokenObtainPairSerializer,
)
from apps.common.permissions import IsAdmin

User = get_user_model()


class LoginView(TokenObtainPairView):
    serializer_class = RoleClaimTokenObtainPairSerializer


class RefreshView(TokenRefreshView):
    pass


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class RegisterDoctorView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DoctorRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = services.register_doctor(**serializer.validated_data)
        return Response(
            {"detail": "Registration received. Awaiting admin approval.", "doctor_id": profile.id},
            status=status.HTTP_201_CREATED,
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.request_password_reset(email=serializer.validated_data["email"])
        # Deliberately the same response regardless of whether the email exists.
        return Response({"detail": "If that account exists, a reset code has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.confirm_password_reset(**serializer.validated_data)
        except services.PasswordResetError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Password has been set. You can now log in."})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)


class AdminDoctorListView(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = DoctorAdminListSerializer
    pagination_class = None

    def get_queryset(self):
        qs = DoctorProfile.objects.select_related("user").all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(registration_status=status_filter)
        return qs.order_by("-created_at")


class AdminDoctorDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        return get_object_or_404(DoctorProfile, pk=pk)

    def get(self, request, user_id):
        profile = self.get_object(user_id)
        return Response(DoctorAdminListSerializer(profile).data)

    def patch(self, request, user_id):
        profile = self.get_object(user_id)
        serializer = DoctorAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.set_doctor_active(profile=profile, is_active=serializer.validated_data["is_active"])
        return Response(DoctorAdminListSerializer(profile).data)

    def delete(self, request, user_id):
        profile = self.get_object(user_id)
        services.soft_delete_doctor(profile=profile)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminDoctorApproveView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        profile = get_object_or_404(DoctorProfile,pk=pk)
        try:
            services.approve_doctor(profile=profile, admin_user=request.user)
        except services.RegistrationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DoctorAdminListSerializer(profile).data)


class AdminDoctorRejectView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        profile = get_object_or_404(DoctorProfile, pk=pk)
        serializer = RejectDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            services.reject_doctor(
                profile=profile, admin_user=request.user, reason=serializer.validated_data.get("reason", "")
            )
        except services.RegistrationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DoctorAdminListSerializer(profile).data)
