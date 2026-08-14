import type { DiseaseSeverity, ScanStatus } from "../api/types";

export function formatDate(iso: string | null | undefined) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function formatDateTime(iso: string | null | undefined) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

export const SEVERITY_LABELS: Record<DiseaseSeverity, string> = {
  NonDemented: "Healthy",
  VeryMildDemented: "Very Mild",
  MildDemented: "Mild",
  ModerateDemented: "Moderate",
};

export const SEVERITY_TONE: Record<DiseaseSeverity, "healthy" | "mild" | "moderate" | "severe"> = {
  NonDemented: "healthy",
  VeryMildDemented: "mild",
  MildDemented: "moderate",
  ModerateDemented: "severe",
};

export const SCAN_STATUS_LABELS: Record<ScanStatus, string> = {
  PENDING: "Queued",
  PROCESSING: "Analyzing",
  COMPLETED: "Completed",
  FAILED: "Failed",
};
