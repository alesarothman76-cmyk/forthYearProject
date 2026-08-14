import { useNavigate, useParams } from "react-router-dom";
import { AlertCircle, ArrowLeft, FileText } from "lucide-react";
import { useScan } from "./hooks";
import { usePatient } from "../patients/hooks";
import { useCreateReport } from "../reports/hooks";
import { ScanStatusBadge } from "./ScanStatusBadge";
import { ClassProbabilityChart } from "./ClassProbabilityChart";
import { SendResultsButton } from "./SendResultsButton";
import { Card } from "../../components/Card";
import { Spinner } from "../../components/Spinner";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { formatDateTime, formatPercent, SEVERITY_LABELS, SEVERITY_TONE } from "../../lib/formatters";

export function ScanDetailPage() {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const id = Number(scanId);
  const { data: scan, isLoading } = useScan(id);
  const { data: patient } = usePatient(scan?.patient);
  const createReport = useCreateReport();

  if (isLoading || !scan) {
    return (
      <div className="flex justify-center py-14">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <button
        onClick={() => navigate(-1)}
        className="flex w-fit items-center gap-1 text-sm text-ink-500 hover:text-ink-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink-900">Scan #{scan.id}</h1>
          <p className="text-sm text-ink-500">Uploaded {formatDateTime(scan.created_at)}</p>
        </div>
        <ScanStatusBadge status={scan.status} />
      </div>

      {(scan.status === "PENDING" || scan.status === "PROCESSING") && (
        <Card className="flex flex-col items-center gap-3 py-10 text-center">
          <Spinner size="lg" />
          <p className="font-medium text-ink-700">
            {scan.status === "PENDING" ? "Queued for processing…" : "Analyzing scan…"}
          </p>
          <p className="max-w-sm text-sm text-ink-500">
            This page updates automatically - no need to refresh.
          </p>
        </Card>
      )}

      {scan.status === "FAILED" && (
        <Card className="flex flex-col gap-3">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-severity-severe" />
            <div>
              <p className="font-medium text-ink-900">This scan couldn't be processed</p>
              <p className="mt-1 text-sm text-ink-500">{scan.error_message}</p>
              <p className="mt-2 text-sm text-ink-500">
                This reflects a technical issue with this specific file, not a finding about the
                patient. Try uploading the scan again.
              </p>
            </div>
          </div>
        </Card>
      )}

      {scan.status === "COMPLETED" && scan.analysis_result && (
        <>
          <Card className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-ink-500">Predicted classification</p>
                <div className="mt-1 flex items-center gap-2">
                  <Badge tone={SEVERITY_TONE[scan.analysis_result.predicted_class]}>
                    {SEVERITY_LABELS[scan.analysis_result.predicted_class]}
                  </Badge>
                  <span className="text-sm text-ink-500">
                    {formatPercent(scan.analysis_result.confidence_score)} confidence
                  </span>
                </div>
              </div>
              <span className="font-mono text-xs text-ink-300">{scan.analysis_result.model_version}</span>
            </div>
            <ClassProbabilityChart result={scan.analysis_result} />
          </Card>

          {/* Heatmap deferred - heatmap_image is currently always null server-side.
              Renders nothing rather than a broken image or an empty box. */}
          {scan.analysis_result.heatmap_image && (
            <Card>
              <p className="mb-2 text-sm font-medium text-ink-700">Analysis heatmap</p>
              <img src={scan.analysis_result.heatmap_image} alt="AI analysis heatmap overlay" className="rounded-md" />
            </Card>
          )}

          <div className="flex items-center gap-3">
            {patient && <SendResultsButton scan={scan} patient={patient} />}
            <Button
              variant="secondary"
              size="sm"
              isLoading={createReport.isPending}
              onClick={async () => {
                const report = await createReport.mutateAsync(scan.id);
                navigate(`/reports/${report.id}`);
              }}
            >
              <FileText className="h-4 w-4" />
              Create report
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
