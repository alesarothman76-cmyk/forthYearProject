import { apiClient } from "../client";
import type { DiseaseSeverity, Gender, Patient, PatientHistory, PatientWritePayload } from "../types";

export interface PatientListParams {
  search?: string;
  gender?: Gender;
  isActive?: "true" | "false" | "all";
  status?: DiseaseSeverity;
}

export async function listPatients(params: PatientListParams = {}) {
  const { data } = await apiClient.get<Patient[]>("/patients/", {
    params: {
      search: params.search || undefined,
      gender: params.gender || undefined,
      is_active: params.isActive ?? undefined,
      status: params.status || undefined,
    },
  });
  return data;
}

export async function getPatient(id: number) {
  const { data } = await apiClient.get<Patient>(`/patients/${id}/`);
  return data;
}

export async function createPatient(payload: PatientWritePayload) {
  const { data } = await apiClient.post<Patient>("/patients/", payload);
  return data;
}

export async function updatePatient(id: number, payload: Partial<PatientWritePayload>) {
  const { data } = await apiClient.patch<Patient>(`/patients/${id}/`, payload);
  return data;
}

export async function archivePatient(id: number) {
  await apiClient.delete(`/patients/${id}/`);
}

export async function getPatientHistory(id: number) {
  const { data } = await apiClient.get<PatientHistory>(`/patients/${id}/history/`);
  return data;
}
