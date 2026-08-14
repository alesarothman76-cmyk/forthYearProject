import { useState } from "react";
import { Users } from "lucide-react";
import { useAdminDoctors, useArchiveDoctor, useSetDoctorActive } from "./hooks";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Badge } from "../../components/Badge";
import { Spinner } from "../../components/Spinner";
import { EmptyState } from "../../components/EmptyState";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { Select } from "../../components/Input";
import { formatDate } from "../../lib/formatters";
import type { DoctorAdmin, RegistrationStatus } from "../../api/types";

const STATUS_TONE: Record<RegistrationStatus, "neutral" | "healthy" | "severe"> = {
  PENDING: "neutral",
  APPROVED: "healthy",
  REJECTED: "severe",
};

export function DoctorManagementPage() {

  const [statusFilter, setStatusFilter] = useState<RegistrationStatus | "">("");
  const { data, isLoading } = useAdminDoctors({ status: statusFilter || undefined });
  const setDoctorActive = useSetDoctorActive();
  const archiveDoctor = useArchiveDoctor();
  const [archiveTarget, setArchiveTarget] = useState<DoctorAdmin | null>(null);

  const doctors = data ?? [];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink-900">Doctors</h1>
          <p className="text-sm text-ink-500">All registered doctor accounts.</p>
        </div>
        <Select
          aria-label="Filter by registration status"
          value={statusFilter}
          onChange={(event) => {
            setStatusFilter(event.target.value as RegistrationStatus | "");
          }}
          className="w-40"
        >
          <option value="">All statuses</option>
          <option value="PENDING">Pending</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
        </Select>
      </div>

      {isLoading && (
        <div className="flex justify-center py-14">
          <Spinner size="lg" />
        </div>
      )}

      {!isLoading && doctors.length === 0 && <EmptyState icon={Users} title="No doctors match this filter" />}

      {doctors.length > 0 && (
        <>
          <Card padded={false}>
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-ink-100 text-xs uppercase tracking-wide text-ink-500">
                  <th className="px-4 py-3 font-medium">Doctor</th>
                  <th className="px-4 py-3 font-medium">License</th>
                  <th className="px-4 py-3 font-medium">Registration</th>
                  <th className="px-4 py-3 font-medium">Account</th>
                  <th className="px-4 py-3 font-medium">Reviewed</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody>
                {doctors.map((doctor) => (
                  <tr key={doctor.id} className="border-b border-ink-100 last:border-0">
                    <td className="px-4 py-3">
                      <p className="font-medium text-ink-900">{doctor.username}</p>
                      <p className="text-xs text-ink-500">{doctor.email}</p>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-ink-500">{doctor.license_number}</td>
                    <td className="px-4 py-3">
                      <Badge tone={STATUS_TONE[doctor.registration_status]}>{doctor.registration_status}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Badge tone={doctor.is_active ? "info" : "neutral"}>
                        {doctor.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-ink-500">{formatDate(doctor.reviewed_at)}</td>
                    <td className="px-4 py-3">
                      {doctor.registration_status === "APPROVED" && (
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="secondary"
                            size="sm"
                            isLoading={setDoctorActive.isPending}
                            onClick={() =>
                              setDoctorActive.mutate({ userId: doctor.id, isActive: !doctor.is_active })
                            }
                          >
                            {doctor.is_active ? "Deactivate" : "Activate"}
                          </Button>
                          <Button variant="danger" size="sm" onClick={() => setArchiveTarget(doctor)}>
                            Archive
                          </Button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </>
      )}

      {archiveTarget && (
        <ConfirmDialog
          title="Archive doctor account"
          message={`This will deactivate and archive ${archiveTarget.username}'s account. This is not reversible through this application - the doctor would need to register again.`}
          confirmLabel="Archive account"
          danger
          isLoading={archiveDoctor.isPending}
          onConfirm={() =>
            archiveDoctor.mutate(archiveTarget.id, {
              onSuccess: () => setArchiveTarget(null),
            })
          }
          onCancel={() => setArchiveTarget(null)}
        />
      )}
    </div>
  );
}
