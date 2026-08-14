import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute, RoleGate } from "./ProtectedRoute";
import { AppLayout } from "./AppLayout";
import { ForbiddenPage } from "./ForbiddenPage";
import { NotFoundPage } from "./NotFoundPage";
import { LoginPage } from "../features/auth/LoginPage";
import { RegisterPage } from "../features/auth/RegisterPage";
import { PasswordResetRequestPage } from "../features/auth/PasswordResetRequestPage";
import { PasswordResetConfirmPage } from "../features/auth/PasswordResetConfirmPage";
import { PatientListPage } from "../features/patients/PatientListPage";
import { PatientDetailPage } from "../features/patients/PatientDetailPage";
import { ScanDetailPage } from "../features/mriScans/ScanDetailPage";
import { ReportListPage } from "../features/reports/ReportListPage";
import { ReportEditorPage } from "../features/reports/ReportEditorPage";
import { DoctorApprovalQueuePage } from "../features/admin/DoctorApprovalQueuePage";
import { DoctorManagementPage } from "../features/admin/DoctorManagementPage";
import { AdminPatientListPage } from "../features/admin/AdminPatientListPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/password-reset/request" element={<PasswordResetRequestPage />} />
      <Route path="/password-reset/confirm" element={<PasswordResetConfirmPage />} />
      <Route path="/forbidden" element={<ForbiddenPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          {/* Doctor area */}
          <Route element={<RoleGate allow={["DOCTOR"]} />}>
            <Route path="/patients" element={<PatientListPage />} />
            <Route path="/patients/:patientId" element={<PatientDetailPage />} />
            <Route path="/scans/:scanId" element={<ScanDetailPage />} />
            <Route path="/reports" element={<ReportListPage />} />
            <Route path="/reports/:reportId" element={<ReportEditorPage />} />
          </Route>

          {/* Admin area */}
          <Route element={<RoleGate allow={["ADMIN"]} />}>
            <Route path="/admin" element={<DoctorApprovalQueuePage />} />
            <Route path="/admin/doctors" element={<DoctorManagementPage />} />
            <Route path="/admin/patients" element={<AdminPatientListPage />} />
          </Route>

          <Route path="/" element={<Navigate to="/patients" replace />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
