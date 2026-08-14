import { apiClient } from "../client";
import type { LoginResponse, Me } from "../types";

export interface RegisterDoctorPayload {
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  license_number: string;
  specialization: string;
  phone_number: string;
}

export async function registerDoctor(payload: RegisterDoctorPayload) {
  const { data } = await apiClient.post<{ detail: string; doctor_id: number }>(
    "/auth/register/",
    payload
  );
  return data;
}

export async function login(username: string, password: string) {
  const { data } = await apiClient.post<LoginResponse>("/auth/login/", { username, password });
  return data;
}

export async function logout(refresh: string) {
  await apiClient.post("/auth/logout/", { refresh });
}

export async function requestPasswordReset(email: string) {
  const { data } = await apiClient.post<{ detail: string }>("/auth/password-reset/request/", {
    email,
  });
  return data;
}

export async function confirmPasswordReset(email: string, code: string, new_password: string) {
  const { data } = await apiClient.post<{ detail: string }>("/auth/password-reset/confirm/", {
    email,
    code,
    new_password,
  });
  return data;
}

export async function getMe() {
  const { data } = await apiClient.get<Me>("/me/");
  return data;
}
