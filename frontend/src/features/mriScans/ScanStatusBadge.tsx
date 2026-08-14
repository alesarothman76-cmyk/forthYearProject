import { Badge } from "../../components/Badge";
import { SCAN_STATUS_LABELS } from "../../lib/formatters";
import type { ScanStatus } from "../../api/types";

const TONE: Record<ScanStatus, "neutral" | "info" | "healthy" | "severe"> = {
  PENDING: "neutral",
  PROCESSING: "info",
  COMPLETED: "healthy",
  FAILED: "severe",
};

export function ScanStatusBadge({ status }: { status: ScanStatus }) {
  return <Badge tone={TONE[status]}>{SCAN_STATUS_LABELS[status]}</Badge>;
}
