import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  approveDoctor,
  archiveDoctor,
  listAdminDoctors,
  listAdminPatients,
  rejectDoctor,
  setDoctorActive,
  type AdminDoctorListParams,
  type AdminPatientListParams,
} from "../../api/endpoints/admin";

export function useAdminDoctors(params: AdminDoctorListParams) {
  return useQuery({
    queryKey: ["admin", "doctors", params],
    queryFn: () => listAdminDoctors(params),
  });
}

export function useAdminPatients(params: AdminPatientListParams) {
  return useQuery({
    queryKey: ["admin", "patients", params],
    queryFn: () => listAdminPatients(params),
  });
}

export function useApproveDoctor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => approveDoctor(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "doctors"] }),
  });
}

export function useRejectDoctor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, reason }: { userId: number; reason: string }) => rejectDoctor(userId, reason),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "doctors"] }),
  });
} 

export function useSetDoctorActive() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, isActive }: { userId: number; isActive: boolean }) =>
      setDoctorActive(userId, isActive),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "doctors"] }),
  });
}

export function useArchiveDoctor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => archiveDoctor(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "doctors"] }),
  });
}
