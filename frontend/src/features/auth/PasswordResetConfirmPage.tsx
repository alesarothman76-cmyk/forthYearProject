import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { confirmPasswordReset } from "../../api/endpoints/auth";
import { Button } from "../../components/Button";
import { Input } from "../../components/Input";
import { ErrorBanner } from "../../components/ErrorBanner";
import { AuthShell } from "./AuthShell";
import type { ApiError } from "../../api/types";

const schema = z
  .object({
    email: z.string().email("Enter a valid email address"),
    code: z.string().length(6, "Enter the 6-digit code"),
    new_password: z.string().min(8, "Password must be at least 8 characters"),
    confirm_password: z.string(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });
type FormValues = z.infer<typeof schema>;

// This one screen serves two real flows: an ordinary "forgot password"
// reset, and a newly-approved doctor setting their first password (both
// use the exact same backend mechanism) - labeled generically rather than
// assuming which case applies, per the frontend plan.
export function PasswordResetConfirmPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await confirmPasswordReset(values.email, values.code, values.new_password);
      navigate("/login", { state: { passwordSet: true } });
    } catch (err) {
      setError((err as ApiError).detail);
    }
  }

  return (
    <AuthShell title="Set your password" subtitle="Enter the code sent to your email along with your new password.">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {error && <ErrorBanner message={error} />}
        <Input label="Email" type="email" error={errors.email?.message} {...register("email")} />
        <Input label="6-digit code" inputMode="numeric" maxLength={6} error={errors.code?.message} {...register("code")} />
        <Input
          label="New password"
          type="password"
          error={errors.new_password?.message}
          {...register("new_password")}
        />
        <Input
          label="Confirm new password"
          type="password"
          error={errors.confirm_password?.message}
          {...register("confirm_password")}
        />
        <Button size="sm"
          className="bg-black hover:bg-zinc-800 text-white"
          color="dark"
        type="submit" isLoading={isSubmitting}>
          Set password
        </Button>
      </form>
    </AuthShell>
  );
}
