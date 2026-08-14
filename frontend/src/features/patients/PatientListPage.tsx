import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Users } from "lucide-react";
import { usePatients } from "./hooks";
import { PatientFilters } from "./PatientFilters";
import { PatientFormModal } from "./PatientFormModal";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { Spinner } from "../../components/Spinner";
import { EmptyState } from "../../components/EmptyState";
import { ErrorBanner } from "../../components/ErrorBanner";
import { Badge } from "../../components/Badge";
import { formatDate, SEVERITY_LABELS, SEVERITY_TONE } from "../../lib/formatters";
import type { PatientListParams } from "../../api/endpoints/patients";
import type { ApiError } from "../../api/types";

export function PatientListPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<PatientListParams>({ isActive: "true" });
  const [showForm, setShowForm] = useState(false);
  const { data: patients, isLoading, isError, error } = usePatients(filters);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink-900">Patients</h1>
          <p className="text-sm text-ink-500">Records you've created.</p>
        </div>
        <Button size="sm"
          className="bg-black hover:bg-zinc-800 text-white"
          color="dark"
          onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4" />
          New patient
        </Button>
      </div>

      <PatientFilters filters={filters} onChange={setFilters} />

      {isLoading && (
        <div className="flex justify-center py-14">
          <Spinner size="lg" />
        </div>
      )}

      {isError && <ErrorBanner message={(error as unknown as ApiError).detail} />}

      {patients && patients.length === 0 && (
        <EmptyState
          icon={Users}
          title="No patients match these filters"
          description="Try adjusting your search or filters, or create a new patient."
          action={<Button onClick={() => setShowForm(true)}>New patient</Button>}
        />
      )}

      {patients && patients.length > 0 && (
        <Card padded={false}>
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-ink-100 text-xs uppercase tracking-wide text-ink-500">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">National ID</th>
                <th className="px-4 py-3 font-medium">Date of birth</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Current status</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((patient) => (
                <tr
                  key={patient.id}
                  onClick={() => navigate(`/patients/${patient.id}`)}
                  className="cursor-pointer border-b border-ink-100 last:border-0 hover:bg-clinical-100/40"
                >
                  <td className="px-4 py-3 font-medium text-ink-900">{patient.full_name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-ink-500">{patient.national_id}</td>
                  <td className="px-4 py-3 text-ink-500">{formatDate(patient.date_of_birth)}</td>
                  <td className="px-4 py-3">
                    <Badge tone={patient.is_active ? "info" : "neutral"}>
                      {patient.is_active ? "Active" : "Archived"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    {patient.current_status ? (
                      <Badge tone={SEVERITY_TONE[patient.current_status]}>
                        {SEVERITY_LABELS[patient.current_status]}
                      </Badge>
                    ) : (
                      <span className="text-ink-300">No scans yet</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {showForm && (
        <PatientFormModal
          onClose={() => setShowForm(false)}
          onSaved={(patient) => {
            setShowForm(false);
            navigate(`/patients/${patient.id}`);
          }}
        />
      )}
    </div>
  );
}
