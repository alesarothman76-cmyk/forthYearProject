import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import type { ApiError, LoginResponse } from "./types";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from "./tokenStore";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export const apiClient = axios.create({ baseURL: BASE_URL });

/** Called by AuthContext on forced logout (refresh itself failed). Set once at app startup. */
let onSessionExpired: (() => void) | null = null;
export function registerSessionExpiredHandler(handler: () => void) {
  onSessionExpired = handler;
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Concurrent 401s should trigger exactly one refresh call, not one per
// failed request - every caller awaits the same in-flight promise.
let refreshInFlight: Promise<string | null> | null = null;

async function performRefresh(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await axios.post<LoginResponse>(`${BASE_URL}/auth/refresh/`, {
      refresh: refreshToken,
    });
    setAccessToken(response.data.access);
    // SimpleJWT rotates refresh tokens - the response may include a new one.
    if ("refresh" in response.data && response.data.refresh) {
      setRefreshToken(response.data.refresh);
    }
    return response.data.access;
  } catch {
    return null;
  }
}

interface RetryableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableConfig | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!refreshInFlight) {
        refreshInFlight = performRefresh().finally(() => {
          refreshInFlight = null;
        });
      }
      const newAccessToken = await refreshInFlight;

      if (newAccessToken) {
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      }

      clearTokens();
      onSessionExpired?.();
    }

    return Promise.reject(normalizeError(error));
  }
);

/** Normalizes every backend error shape into one consistent ApiError. */
function normalizeError(error: AxiosError): ApiError {
  const data = error.response?.data as
    | { error?: { detail?: unknown; status_code?: number } }
    | Record<string, unknown>
    | undefined;

  const status = error.response?.status ?? 0;

  if (data && typeof data === "object" && "error" in data && data.error) {
    const detail = (data.error as { detail?: unknown }).detail;
    if (typeof detail === "string") {
      return { detail, status_code: status };
    }
    if (detail && typeof detail === "object") {
      // DRF field-level validation errors nested under error.detail
      return {
        detail: "Please correct the highlighted fields.",
        status_code: status,
        fieldErrors: detail as Record<string, string[]>,
      };
    }
  }

  // Fallback for network errors, or responses that don't match the
  // documented {error: {detail, status_code}} shape.
  return {
    detail: error.message || "Something went wrong. Please try again.",
    status_code: status,
  };
}
