import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createReport,
  deleteReport,
  downloadReportPdf,
  finalizeReport,
  getReport,
  listReports,
  updateReportNotes,
  type ReportListParams,
} from "../../api/endpoints/reports";

export function useReports(params: ReportListParams = {}) {
  return useQuery({
    queryKey: ["reports", params],
    queryFn: () => listReports(params),
  });
}

export function useReport(id: number | undefined) {
  return useQuery({
    queryKey: ["report", id],
    queryFn: () => getReport(id as number),
    enabled: id !== undefined,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (mriScanId: number) => createReport(mriScanId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}

export function useUpdateReportNotes(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (notes: string) => updateReportNotes(id, notes),
    onSuccess: (report) => {
      queryClient.setQueryData(["report", id], report);
    },
  });
}

export function useFinalizeReport(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => finalizeReport(id),
    onSuccess: (report) => {
      queryClient.setQueryData(["report", id], report);
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteReport(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}

export function useDownloadReportPdf() {
  return useMutation({
    mutationFn: async (id: number) => {
      const blob = await downloadReportPdf(id);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `report_${id}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    },
  });
}
