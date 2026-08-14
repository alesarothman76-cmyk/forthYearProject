import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, FileCheck2 } from "lucide-react";
import { useReport, useUpdateReportNotes, useFinalizeReport, useDownloadReportPdf } from "./hooks";
import { useScan } from "../mriScans/hooks";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Textarea } from "../../components/Input";
import { Badge } from "../../components/Badge";
import { Spinner } from "../../components/Spinner";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { formatDateTime, formatPercent, SEVERITY_LABELS, SEVERITY_TONE } from "../../lib/formatters";
import { toast } from "sonner";

export function ReportEditorPage() {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const id = Number(reportId);

  const { data: report, isLoading } = useReport(id);
  const { data: scan } = useScan(report?.mri_scan);
  const updateNotes = useUpdateReportNotes(id);
  const finalizeReport = useFinalizeReport(id);
  const downloadPdf = useDownloadReportPdf();

  const [notes, setNotes] = useState<string | null>(null);
  const [showFinalizeConfirm, setShowFinalizeConfirm] = useState(false);

  if (isLoading || !report) {
    return (
      <div className="flex justify-center py-14">
        <Spinner size="lg" />
      </div>
    );
  }

  const isDraft = report.status === "DRAFT";
  const currentNotes = notes ?? report.notes;
  const isDirty = notes !== null && notes !== report.notes;

  return (
    <div className="flex flex-col gap-6">
      <button
        className="bg-black hover:bg-zinc-800 text-white"
        color="dark"
        onClick={() => navigate(-1)}
        >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink-900">Report for {report.patient_name}</h1>
          <p className="text-sm text-ink-500">Scan #{report.mri_scan}</p>
        </div>
        <Badge tone={isDraft ? "neutral" : "healthy"}>{isDraft ? "Draft" : "Finalized"}</Badge>
      </div>

      {scan?.analysis_result && (
        <Card>
          <p className="text-xs uppercase tracking-wide text-ink-500">AI analysis result</p>
          <div className="mt-2 flex items-center gap-2">
            <Badge tone={SEVERITY_TONE[scan.analysis_result.predicted_class]}>
              {SEVERITY_LABELS[scan.analysis_result.predicted_class]}
            </Badge>
            <span className="text-sm text-ink-500">
              {formatPercent(scan.analysis_result.confidence_score)} confidence
            </span>
          </div>
        </Card>
      )}

      <Card>
        <p className="mb-2 text-sm font-medium text-ink-700">Clinical notes</p>
        {isDraft ? (
          <>
            <Textarea
              rows={10}
              value={currentNotes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Enter your clinical assessment and notes for this report…"
            />
            <div className="mt-3 flex justify-end">
              <Button
              className="bg-black hover:bg-zinc-800 text-white"
              color="dark"
                disabled={!isDirty}
                isLoading={updateNotes.isPending}
                onClick={() =>
                  updateNotes.mutate(currentNotes, {
                    onSuccess: () => {
                      setNotes(null);
                      toast.success("Notes saved");
                    },
                  })
                }
              >
                Save changes
              </Button>
            </div>
          </>
        ) : (
          // Notes rendered read-only; no Save button anywhere in this
          // branch at all - removed, not disabled, so the UI can never
          // imply an edit that will silently fail server-side.
          <p className="whitespace-pre-wrap text-sm text-ink-700">{report.notes || "(No notes provided.)"}</p>
        )}
      </Card>

      <div className="flex items-center gap-3">
        {isDraft ? (
          <Button 
          className="bg-black hover:bg-zinc-800 text-white"
          color="dark"
          onClick={() => setShowFinalizeConfirm(true)}>
            <FileCheck2 className="h-4 w-4" />
            Finalize report
          </Button>
        ) : (
          <Button
            className="bg-black hover:bg-zinc-800 text-white"
            color="dark"
            isLoading={downloadPdf.isPending}
            onClick={() => downloadPdf.mutate(report.id)}
          >
            <Download className="h-4 w-4" />
            Download PDF
          </Button>
        )}
        {report.finalized_at && (
          <span className="text-xs text-ink-500">Finalized {formatDateTime(report.finalized_at)}</span>
        )}
      </div>

      {showFinalizeConfirm && (
        <ConfirmDialog
          title="Finalize report"
          message="Finalizing generates a permanent PDF and locks this report. Notes can no longer be edited or deleted afterward. This action cannot be undone."
          confirmLabel="Finalize"
          danger
          isLoading={finalizeReport.isPending}
          onConfirm={() =>
            finalizeReport.mutate(undefined, {
              onSuccess: () => setShowFinalizeConfirm(false),
            })
          }
          onCancel={() => setShowFinalizeConfirm(false)}
        />
      )}
    </div>
  );
}
