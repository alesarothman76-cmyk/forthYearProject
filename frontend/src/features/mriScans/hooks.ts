import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getMriScan, listMriScans, sendScanResults, uploadMriScan } from "../../api/endpoints/mriScans";
import type { MRIScan } from "../../api/types";

/**
 * Written to be correct under both the backend's current synchronous
 * execution and its planned future asynchronous (Celery) execution,
 * without modification. Today, the first fetch after upload already
 * returns a terminal status, so refetchInterval evaluates to false
 * immediately and this never actually polls. Once the backend returns
 * PENDING immediately and processes in the background, this same code
 * starts polling automatically - the branch was always written against
 * the real status field, not an assumption about which behavior is
 * currently true.
 */
export function useScan(scanId: number | undefined) {
  return useQuery({
    queryKey: ["scan", scanId],
    queryFn: () => getMriScan(scanId as number),
    enabled: scanId !== undefined,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "PENDING" || status === "PROCESSING" ? 2000 : false;
    },
  });
}

export function useScansForPatient(patientId: number | undefined) {
  return useQuery({
    queryKey: ["scans", { patient: patientId }],
    queryFn: () => listMriScans(patientId),
    enabled: patientId !== undefined,
  });
}

export function useUploadScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      patientId,
      file,
      onProgress,
    }: {
      patientId: number;
      file: File;
      onProgress?: (percent: number) => void;
    }) => uploadMriScan(patientId, file, onProgress),
    onSuccess: (scan: MRIScan) => {
      queryClient.invalidateQueries({ queryKey: ["scans", { patient: scan.patient }] });
      queryClient.invalidateQueries({ queryKey: ["patient", scan.patient, "history"] });
      queryClient.setQueryData(["scan", scan.id], scan);
    },
  });
}

export function useSendScanResults(scanId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => sendScanResults(scanId),
    onSuccess: (scan) => {
      queryClient.setQueryData(["scan", scanId], scan);
    },
  });
}
