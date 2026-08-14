import { apiClient } from "../client";
import type { Report } from "../types";

export interface ReportListParams {
  patient?: number;
  mriScan?: number;
}

export async function listReports(params: ReportListParams = {}) {
  const { data } = await apiClient.get<Report[]>("/reports/", {
    params: { patient: params.patient, mri_scan: params.mriScan },
  });
  return data;
}

export async function getReport(id: number) {
  const { data } = await apiClient.get<Report>(`/reports/${id}/`);
  return data;
}

export async function createReport(mriScanId: number, notes = "") {
  const { data } = await apiClient.post<Report>("/reports/", { mri_scan: mriScanId, notes });
  return data;
}

export async function updateReportNotes(id: number, notes: string) {
  const { data } = await apiClient.patch<Report>(`/reports/${id}/`, { notes });
  return data;
}

export async function finalizeReport(id: number) {
  const { data } = await apiClient.post<Report>(`/reports/${id}/finalize/`);
  return data;
}

export async function deleteReport(id: number) {
  await apiClient.delete(`/reports/${id}/`);
}

export async function downloadReportPdf(id: number) {
  const response = await apiClient.get(`/reports/${id}/pdf/`, { responseType: "blob" });
  return response.data as Blob;
}
