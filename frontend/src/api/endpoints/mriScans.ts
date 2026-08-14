import { apiClient } from "../client";
import type { MRIScan } from "../types";

export async function listMriScans(patientId?: number) {
  const { data } = await apiClient.get<MRIScan[]>("/mri-scans/", {
    params: { patient: patientId },
  });
  return data;
}

export async function getMriScan(id: number) {
  const { data } = await apiClient.get<MRIScan>(`/mri-scans/${id}/`);
  return data;
}

export async function uploadMriScan(
  patientId: number,
  file: File,
  onUploadProgress?: (percent: number) => void
) {
  const formData = new FormData();
  formData.append("patient", String(patientId));
  formData.append("file", file);

  const { data } = await apiClient.post<MRIScan>("/mri-scans/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (onUploadProgress && event.total) {
        onUploadProgress(Math.round((event.loaded / event.total) * 100));
      }
    },
  });
  return data;
}

export async function sendScanResults(scanId: number) {
  const { data } = await apiClient.post<MRIScan>(`/mri-scans/${scanId}/send-results/`);
  return data;
}
