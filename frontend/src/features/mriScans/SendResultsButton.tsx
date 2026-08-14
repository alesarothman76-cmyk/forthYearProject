import { useState } from "react";
import { Mail } from "lucide-react";
import { Button } from "../../components/Button";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { useSendScanResults } from "./hooks";
import { formatDateTime } from "../../lib/formatters";
import type { MRIScan, Patient } from "../../api/types";

export function SendResultsButton({ scan, patient }: { scan: MRIScan; patient: Patient }) {
  const [showConfirm, setShowConfirm] = useState(false);
  const sendResults = useSendScanResults(scan.id);

  if (scan.status !== "COMPLETED") return null;

  const hasEmail = Boolean(patient.email);
  const alreadySent = Boolean(scan.results_sent_at);

  return (
    <div className="flex flex-col items-start gap-1">
      <Button
        variant="secondary"
        size="sm"
        disabled={!hasEmail}
        title={hasEmail ? undefined : "Add an email address to this patient's profile to send results"}
        onClick={() => setShowConfirm(true)}
      >
        <Mail className="h-4 w-4" />
        {alreadySent ? "Resend results" : "Send results to patient"}
      </Button>
      {alreadySent && (
        <span className="text-xs text-ink-500">Last sent {formatDateTime(scan.results_sent_at)}</span>
      )}

      {showConfirm && (
        <ConfirmDialog
          title="Send results to patient"
          message={`This will email a summary of this scan's AI result directly to ${patient.email}. This is sent as plain, unencrypted email - not a secure patient portal - so only send results you're comfortable transmitting this way.`}
          confirmLabel="Send email"
          isLoading={sendResults.isPending}
          onConfirm={() => sendResults.mutate(undefined, { onSuccess: () => setShowConfirm(false) })}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  );
}
