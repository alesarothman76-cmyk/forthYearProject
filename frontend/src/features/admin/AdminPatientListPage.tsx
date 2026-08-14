import { useState } from "react";
import { Search, Users } from "lucide-react";
import { useAdminDoctors, useAdminPatients } from "./hooks";
import { Card } from "../../components/Card";
import { Spinner } from "../../components/Spinner";
import { EmptyState } from "../../components/EmptyState";
import { Badge } from "../../components/Badge";
import { Pagination } from "../../components/Pagination";
import { Select } from "../../components/Input";
import { formatDate, SEVERITY_LABELS, SEVERITY_TONE } from "../../lib/formatters";
import type { DoctorAdmin } from "../../api/types";

// Deliberately no edit or delete affordance anywhere on this page - the
// backend exposes no such capability here (Admin oversight is read-only
// by design), so the UI doesn't imply one exists either.
export function AdminPatientListPage() {
  const [search, setSearch] = useState("");
  const [doctorId, setDoctorId] = useState<number | "">("");
  const [isActive, setIsActive] = useState<"true" | "false" | "all">("all");
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAdminPatients({ search: search || undefined, doctorId: doctorId || undefined, isActive, page });
  const { data: doctors } = useAdminDoctors({});

  const patients = data?.results ?? [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-900">Patients</h1>
        <p className="text-sm text-ink-500">
          Read-only view across all doctors. Medical history is not shown here.
        </p>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="relative flex-1 min-w-50">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-300" />
          <input
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
            placeholder="Search by name or national ID"
            className="w-full rounded-md border border-ink-100 py-2 pl-9 pr-3 text-sm focus:border-clinical-500"
          />
        </div>
        <Select
          aria-label="Filter by doctor"
          value={doctorId}
          onChange={(event) => {
            setDoctorId(event.target.value ? Number(event.target.value) : "");
            setPage(1);
          }}
          className="w-48"
        >
          <option value="">All doctors</option>
          {doctors?.map((doctor: DoctorAdmin) => (
            <option key={doctor.id} value={doctor.id}>
              {doctor.username} @{doctor.license_number}
            </option>
          ))}
        </Select>
        <Select
          aria-label="Filter by record status"
          value={isActive}
          onChange={(event) => {
            setIsActive(event.target.value as "true" | "false" | "all");
            setPage(1);
          }}
          className="w-36"
        >
          <option value="all">All records</option>
          <option value="true">Active</option>
          <option value="false">Archived</option>
        </Select>
      </div>

      {isLoading && (
        <div className="flex justify-center py-14">
          <Spinner size="lg" />
        </div>
      )}

      {!isLoading && patients.length === 0 && <EmptyState icon={Users} title="No patients match this search" />}

      {patients.length > 0 && (
        <>
          <Card padded={false}>
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-ink-100 text-xs uppercase tracking-wide text-ink-500">
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">National ID</th>
                  <th className="px-4 py-3 font-medium">Doctor</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Record</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id} className="border-b border-ink-100 last:border-0">
                    <td className="px-4 py-3 font-medium text-ink-900">{patient.full_name}</td>
                    <td className="px-4 py-3 font-mono text-xs text-ink-500">{patient.national_id}</td>
                    <td className="px-4 py-3 text-ink-700">
                      {patient.created_by_doctor_name}
                      <span className="ml-1 text-xs text-ink-500">@{patient.created_by_doctor_username}</span>
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
                    <td className="px-4 py-3">
                      <Badge tone={patient.is_active ? "info" : "neutral"}>
                        {patient.is_active ? "Active" : "Archived"}
                      </Badge>
                      <span className="ml-2 text-xs text-ink-500">{formatDate(patient.created_at)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
          {data && (
            <Pagination
              count={data.count}
              hasNext={Boolean(data.next)}
              hasPrevious={Boolean(data.previous)}
              onNext={() => setPage((p) => p + 1)}
              onPrevious={() => setPage((p) => Math.max(1, p - 1))}
            />
          )}
        </>
      )}
    </div>
  );
}
