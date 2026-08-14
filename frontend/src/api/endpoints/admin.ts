import { apiClient } from "../client";
import type { AdminPatient, DoctorAdmin, DiseaseSeverity, Paginated, RegistrationStatus } from "../types";

export interface AdminDoctorListParams {
  status?: RegistrationStatus;
}
 
export async function listAdminDoctors(params: AdminDoctorListParams = {}) {
  const { data } = await apiClient.get<DoctorAdmin[]>("/admin/doctors/", {
    params: { status: params.status},
  });
  return data;
}

export async function approveDoctor(userId: number) {
  const { data } = await apiClient.post<DoctorAdmin>(`/admin/doctors/${userId}/approve/`);
  return data;
}

export async function rejectDoctor(userId: number, reason = "") {
  const { data } = await apiClient.post<DoctorAdmin>(`/admin/doctors/${userId}/reject/`, { reason });
  return data;
}

export async function setDoctorActive(userId: number, isActive: boolean) {
  const { data } = await apiClient.patch<DoctorAdmin>(`/admin/doctors/${userId}/`, {
    is_active: isActive,
  });
  return data;
}

export async function archiveDoctor(userId: number) {
  await apiClient.delete(`/admin/doctors/${userId}/`);
}

export interface AdminPatientListParams {
  search?: string;
  doctorId?: number;
  isActive?: "true" | "false" | "all";
  page?: number;
}

export async function listAdminPatients(params: AdminPatientListParams = {}) {
  const apiParams: Record<string, unknown> = {
    search: params.search,
    doctor_id: params.doctorId,
    page: params.page,
  };
  if (params.isActive && params.isActive !== "all") {
    apiParams.is_active = params.isActive;
  }
  const { data } = await apiClient.get<Paginated<AdminPatient>>("/admin/patients/", {
    params: apiParams,
  });
  return data;
}
