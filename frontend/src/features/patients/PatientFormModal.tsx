import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Modal } from "../../components/Modal";
import { Button } from "../../components/Button";
import { Input, Select, Textarea } from "../../components/Input";
import { ErrorBanner } from "../../components/ErrorBanner";
import { useCreatePatient, useUpdatePatient } from "./hooks";
import type { ApiError, Patient } from "../../api/types";
import { useState } from "react";

const createSchema = z.object({
  national_id: z.string().min(1, "National ID is required"),
  full_name: z.string().min(1, "Full name is required"),
  date_of_birth: z.string().min(1, "Date of birth is required"),
  gender: z.enum(["MALE", "FEMALE"]),
  email: z.string().email("Enter a valid email address").or(z.literal("")).optional(),
  medical_history: z.string().optional(),
});
type FormValues = z.infer<typeof createSchema>;

export function PatientFormModal({
  patient,
  onClose,
  onSaved,
}: {
  patient?: Patient;
  onClose: () => void;
  onSaved: (patient: Patient) => void;
}) {
  const isEdit = Boolean(patient);
  const [error, setError] = useState<string | null>(null);
  const createMutation = useCreatePatient();
  const updateMutation = useUpdatePatient(patient?.id ?? -1);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(createSchema),
    defaultValues: patient
      ? {
          national_id: patient.national_id,
          full_name: patient.full_name,
          date_of_birth: patient.date_of_birth,
          gender: patient.gender,
          email: patient.email,
          medical_history: patient.medical_history,
        }
      : { gender: "FEMALE" },
  });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      if (isEdit && patient) {
        // national_id is immutable server-side and intentionally omitted
        // from the update payload here, not just disabled in the UI.
        const { national_id: _nationalId, ...editable } = values;
        void _nationalId;
        const updated = await updateMutation.mutateAsync(editable);
        onSaved(updated);
      } else {
        const created = await createMutation.mutateAsync(values);
        onSaved(created);
      }
    } catch (err) {
      setError((err as ApiError).detail);
    }
  }

  return (
    <Modal
      title={isEdit ? "Edit patient" : "New patient"}
      onClose={onClose}
      footer={
        <>
          <Button 
            type="submit" form="patient-form" isLoading={isSubmitting} size="sm"
            className="bg-black hover:bg-zinc-800 text-white"
            color="dark">
            {isEdit ? "Save changes" : "Create patient"}
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
        </>
      }
    >
      <form id="patient-form" onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {error && <ErrorBanner message={error} />}
        <Input
          label="National ID"
          disabled={isEdit}
          hint={isEdit ? "National ID cannot be changed after creation." : undefined}
          error={errors.national_id?.message}
          {...register("national_id")}
        />
        <Input label="Full name" error={errors.full_name?.message} {...register("full_name")} />
        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Date of birth"
            type="date"
            error={errors.date_of_birth?.message}
            {...register("date_of_birth")}
          />
          <Select label="Gender" error={errors.gender?.message} {...register("gender")}>
            <option value="FEMALE">Female</option>
            <option value="MALE">Male</option>
          </Select>
        </div>
        <Input
          label="Email"
          type="email"
          hint="Optional - required only to send this patient their result summary by email."
          error={errors.email?.message}
          {...register("email")}
        />
        <Textarea
          label="Medical history"
          rows={4}
          error={errors.medical_history?.message}
          {...register("medical_history")}
        />
      </form>
    </Modal>
  );
}
