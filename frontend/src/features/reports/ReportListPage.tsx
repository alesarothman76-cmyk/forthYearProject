import { useNavigate } from "react-router-dom";
import { FileText } from "lucide-react";
import { useReports } from "./hooks";
import { Card } from "../../components/Card";
import { Spinner } from "../../components/Spinner";
import { EmptyState } from "../../components/EmptyState";
import { Badge } from "../../components/Badge";
import { formatDateTime } from "../../lib/formatters";

export function ReportListPage() {
  const navigate = useNavigate();
  const { data: reports, isLoading } = useReports();

  if (isLoading) {
    return (
      <div className="flex justify-center py-14">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-900">Reports</h1>
        <p className="text-sm text-ink-500">All reports you've authored.</p>
      </div>

      {reports && reports.length === 0 && (
        <EmptyState
          icon={FileText}
          title="No reports yet"
          description="Create a report from a completed scan's detail page."
        />
      )}

      {reports && reports.length > 0 && (
        <div className="flex flex-col gap-3">
          {reports.map((report) => (
            <Card
              key={report.id}
              className="flex cursor-pointer items-center justify-between hover:border-clinical-300"
              onClick={() => navigate(`/reports/${report.id}`)}
            >
              <div>
                <p className="text-sm font-medium text-ink-900">{report.patient_name}</p>
                <p className="mt-0.5 text-xs text-ink-500">
                  Scan #{report.mri_scan} · Created {formatDateTime(report.created_at)}
                </p>
              </div>
              <Badge tone={report.status === "DRAFT" ? "neutral" : "healthy"}>
                {report.status === "DRAFT" ? "Draft" : "Finalized"}
              </Badge>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
