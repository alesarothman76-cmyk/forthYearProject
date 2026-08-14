import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import { registerDoctor } from "../../api/endpoints/auth";
import { Button } from "../../components/Button";
import { Input } from "../../components/Input";
import { ErrorBanner } from "../../components/ErrorBanner";
import { AuthShell } from "./AuthShell";
import { CheckCircle2 } from "lucide-react";
import type { ApiError } from "../../api/types";

const schema = z.object({
  username: z.string().min(1, "Username is required"),
  email: z.string().email("Enter a valid email address"),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  license_number: z.string().min(1, "License number is required"),
  specialization: z.string().min(1, "Specialization is required"),
  phone_number: z.string().min(1, "Phone number is required"),
});
type FormValues = z.infer<typeof schema>;

export function RegisterPage() {
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await registerDoctor(values);
      setSubmitted(true);
    } catch (err) {
      setError((err as ApiError).detail);
    }
  }

  if (submitted) {
    return (
      <AuthShell title="Registration received">
        <div className="flex flex-col items-center gap-3 text-center">
          <CheckCircle2 className="h-10 w-10 text-severity-healthy" />
          <p className="text-sm text-ink-700">
            Your registration is pending review by the hospital administrator. You'll receive an
            email with a password-setup code once it's approved.
          </p>
          <Link to="/login" className="mt-2 text-sm text-clinical-600 hover:underline">
            Back to sign in
          </Link>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell title="Request a doctor account" subtitle="Your registration will be reviewed by the hospital administrator.">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {error && <ErrorBanner message={error} />}
        <div className="grid grid-cols-2 gap-3">
          <Input label="First name" error={errors.first_name?.message} {...register("first_name")} />
          <Input label="Last name" error={errors.last_name?.message} {...register("last_name")} />
        </div>
        <Input label="Username" error={errors.username?.message} {...register("username")} />
        <Input label="Email" type="email" error={errors.email?.message} {...register("email")} />
        <Input label="License number" error={errors.license_number?.message} {...register("license_number")} />
        <Input label="Specialization" error={errors.specialization?.message} {...register("specialization")} />
        <Input label="Phone number" error={errors.phone_number?.message} {...register("phone_number")} />
        <Button type="submit" isLoading={isSubmitting} size="sm"
          className="bg-black hover:bg-zinc-800 text-white"
          color="dark">
          Submit registration
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-ink-500">
        Already approved?{" "}
        <Link to="/login" className="text-clinical-600 hover:underline">
          Sign in
        </Link>
      </p>
    </AuthShell>
  );
}
