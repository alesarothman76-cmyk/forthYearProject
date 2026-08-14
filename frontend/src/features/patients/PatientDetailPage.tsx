import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Archive, ArrowLeft, FileImage, Pencil } from "lucide-react";
import { usePatient, usePatientHistory, useArchivePatient } from "./hooks";
import { PatientFormModal } from "./PatientFormModal";
import { ScanUploadForm } from "../mriScans/ScanUploadForm";
import { ScanStatusBadge } from "../mriScans/ScanStatusBadge";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { Spinner } from "../../components/Spinner";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { EmptyState } from "../../components/EmptyState";
import { formatDate, formatDateTime, SEVERITY_LABELS, SEVERITY_TONE } from "../../lib/formatters";

export function PatientDetailPage() {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const id = Number(patientId);

  const { data: patient, isLoading } = usePatient(id);
  const { data: history } = usePatientHistory(id);
  const archivePatient = useArchivePatient();

  const [showEdit, setShowEdit] = useState(false);
  const [showArchiveConfirm, setShowArchiveConfirm] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  if (isLoading || !patient) {
    return (
      <div className="flex justify-center py-14">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <button
        className="bg-black hover:bg-zinc-800 text-white"
         color="dark"
        onClick={() => navigate("/patients")}
      >
        {/* className=" flex w-fit items-center gap-1 text-sm text-ink-500 hover:text-ink-900" */}
        <ArrowLeft className="h-4 w-4" />
        All patients
      </button>

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold text-ink-900">{patient.full_name}</h1>
            {!patient.is_active && <Badge tone="neutral">Archived</Badge>}
            {patient.current_status && (
              <Badge tone={SEVERITY_TONE[patient.current_status]}>{SEVERITY_LABELS[patient.current_status]}</Badge>
            )}
          </div>
          <p className="mt-1 font-mono text-xs text-ink-500">{patient.national_id}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => setShowEdit(true)}>
            <Pencil className="h-4 w-4" />
            Edit
          </Button>
          {patient.is_active && (
            <Button variant="secondary" size="sm" onClick={() => setShowArchiveConfirm(true)}>
              <Archive className="h-4 w-4" />
              Archive
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card>
          <p className="text-xs uppercase tracking-wide text-ink-500">Date of birth</p>
          <p className="mt-1 text-sm text-ink-900">{formatDate(patient.date_of_birth)}</p>
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-wide text-ink-500">Gender</p>
          <p className="mt-1 text-sm text-ink-900">{patient.gender === "MALE" ? "Male" : "Female"}</p>
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-wide text-ink-500">Email</p>
          <p className="mt-1 text-sm text-ink-900">{patient.email || "—"}</p>
        </Card>
      </div>

      {patient.medical_history && (
        <Card>
          <p className="text-xs uppercase tracking-wide text-ink-500">Medical history</p>
          <p className="mt-1 whitespace-pre-wrap text-sm text-ink-700">{patient.medical_history}</p>
        </Card>
      )}

      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-ink-900">Scan history</h2>
        <Button className="bg-black hover:bg-zinc-800 text-white"
         color="dark"
          onClick={() => setShowUpload((v) => !v)}>
          {showUpload ? "Cancel" : "Upload new scan"}
        </Button>
      </div>

      {showUpload && (
        <Card>
          <ScanUploadForm patientId={patient.id} />
        </Card>
      )}

      {history && history.scans.length === 0 && (
        <EmptyState icon={FileImage} title="No scans yet" description="Upload an MRI scan to begin AI analysis." />
      )}

      {history && history.scans.length > 0 && (
        <div className="flex flex-col gap-3">
          {history.scans.map((scan) => (
            <Card
              key={scan.id}
              className="flex cursor-pointer items-center justify-between hover:border-clinical-300"
              padded
            >
              <div onClick={() => navigate(`/scans/${scan.id}`)} className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-ink-900">Scan #{scan.id}</span>
                  <ScanStatusBadge status={scan.status} />
                  {scan.analysis_result && (
                    <Badge tone={SEVERITY_TONE[scan.analysis_result.predicted_class]}>
                      {SEVERITY_LABELS[scan.analysis_result.predicted_class]}
                    </Badge>
                  )}
                </div>
                <p className="mt-1 text-xs text-ink-500">
                  Uploaded {formatDateTime(scan.created_at)}
                  {scan.reports.length > 0 && ` · ${scan.reports.length} report${scan.reports.length > 1 ? "s" : ""}`}
                </p>
              </div>
            </Card>
          ))}
        </div>
      )}

      {showEdit && (
        <PatientFormModal patient={patient} onClose={() => setShowEdit(false)} onSaved={() => setShowEdit(false)} />
      )}

      {showArchiveConfirm && (
        <ConfirmDialog
          title="Archive patient"
          message={`This will archive ${patient.full_name}'s record. It can still be viewed but will no longer appear in your active patient list. This does not delete any clinical data.`}
          confirmLabel="Archive"
          danger
          isLoading={archivePatient.isPending}
          onConfirm={() =>
            archivePatient.mutate(patient.id, {
              onSuccess: () => {
                setShowArchiveConfirm(false);
                navigate("/patients");
              },
            })
          }
          onCancel={() => setShowArchiveConfirm(false)}
        />
      )}
    </div>
  );
}
