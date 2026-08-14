import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  archivePatient,
  createPatient,
  getPatient,
  getPatientHistory,
  listPatients,
  updatePatient,
  type PatientListParams,
} from "../../api/endpoints/patients";
import type { PatientWritePayload } from "../../api/types";

export function usePatients(params: PatientListParams) {
  return useQuery({
    queryKey: ["patients", params],
    queryFn: () => listPatients(params),
  });
}

export function usePatient(id: number | undefined) {
  return useQuery({
    queryKey: ["patient", id],
    queryFn: () => getPatient(id as number),
    enabled: id !== undefined,
  });
}

export function usePatientHistory(id: number | undefined) {
  return useQuery({
    queryKey: ["patient", id, "history"],
    queryFn: () => getPatientHistory(id as number),
    enabled: id !== undefined,
  });
}

export function useCreatePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: PatientWritePayload) => createPatient(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });
}

export function useUpdatePatient(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Partial<PatientWritePayload>) => updatePatient(id, payload),
    onSuccess: (patient) => {
      queryClient.invalidateQueries({ queryKey: ["patients"] });
      queryClient.setQueryData(["patient", id], patient);
    },
  });
}

export function useArchivePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => archivePatient(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });
}
