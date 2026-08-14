import { useState } from "react";
import { ShieldCheck, Check, X } from "lucide-react";
import { useAdminDoctors, useApproveDoctor, useRejectDoctor } from "./hooks";
import { Card } from "../../components/Card";
import { Button } from "../../components/Button";
import { Spinner } from "../../components/Spinner";
import { EmptyState } from "../../components/EmptyState";
import { Modal } from "../../components/Modal";
import { Textarea } from "../../components/Input";

import { formatDate } from "../../lib/formatters";
import { toast } from "sonner";
import type { DoctorAdmin } from "../../api/types";

export function DoctorApprovalQueuePage() {
  const { data, isLoading } = useAdminDoctors({ status: "PENDING" });
  const approveDoctor = useApproveDoctor();
  const [rejectTarget, setRejectTarget] = useState<DoctorAdmin | null>(null);

  if (isLoading) {
    return (
      <div className="flex justify-center py-14">
        <Spinner size="lg" />
      </div>
    );
  }

  const doctors = data ?? [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-ink-900">Approval queue</h1>
        <p className="text-sm text-ink-500">Doctor registrations awaiting review.</p>
      </div>

      {doctors.length === 0 && (
        <EmptyState icon={ShieldCheck} title="No pending registrations" description="You're all caught up." />
      )}

      {doctors.length > 0 && (
        <>
          <div className="flex flex-col gap-3">
            {doctors.map((doctor) => (
              <Card key={doctor.id}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-ink-900">{doctor.username}</p>
                    <p className="text-sm text-ink-500">{doctor.email}</p>
                    <div className="mt-2 grid grid-cols-2 gap-x-6 gap-y-1 text-sm text-ink-700">
                      <span>
                        <span className="text-ink-500">License: </span>
                        {doctor.license_number}
                      </span>
                      <span>
                        <span className="text-ink-500">Specialization: </span>
                        {doctor.specialization}
                      </span>
                      <span>
                        <span className="text-ink-500">Phone: </span>
                        {doctor.phone_number}
                      </span>
                      <span>
                        <span className="text-ink-500">Submitted: </span>
                        {formatDate(doctor.created_at)}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      isLoading={approveDoctor.isPending}
                      className="bg-black hover:bg-zinc-800 text-white"
                      color="dark"
                      onClick={() =>
                        approveDoctor.mutate(doctor.id, {
                          onSuccess: () => toast.success(`${doctor.username} approved`),
                        })
                      }
                    >
                      <Check className="h-4 w-4" />
                      Approve
                    </Button>

                    <Button
                      variant="danger"
                      size="sm"
                      className="bg-black hover:bg-zinc-800 text-white"
                      color="dark"
                      onClick={() => setRejectTarget(doctor)}
                    >
                      <X className="h-4 w-4" />
                      Reject
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
           
        </>
      )}

      {rejectTarget && <RejectDialog doctor={rejectTarget} onClose={() => setRejectTarget(null)} />}
    </div>
  );
}

function RejectDialog({ doctor, onClose }: { doctor: DoctorAdmin; onClose: () => void }) {
  const [reason, setReason] = useState("");
  const rejectDoctor = useRejectDoctor();

  return (
    <Modal
      title={`Reject ${doctor.username}`}
      onClose={onClose}
      footer={
        <>
         
          <Button
          size="sm"
          className="bg-black hover:bg-zinc-800 text-white"
          color="dark"
            variant="danger"
            isLoading={rejectDoctor.isPending}
            onClick={() =>
              rejectDoctor.mutate(
                { userId: doctor.id, reason },
                {
                  onSuccess: () => {
                    toast.success(`${doctor.username} rejected`);
                    onClose();
                  },
                }
              )
            }
          >
            Reject registration
          </Button>
           <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
        </>
      }
    >
      <Textarea
        label="Reason (optional)"
        rows={3}
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        placeholder="e.g. License number could not be verified"
      />
    </Modal>
  );
}
