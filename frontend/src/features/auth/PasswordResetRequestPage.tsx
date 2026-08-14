import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { requestPasswordReset } from "../../api/endpoints/auth";
import { Button } from "../../components/Button";
import { Input } from "../../components/Input";
import { AuthShell } from "./AuthShell";

const schema = z.object({ email: z.string().email("Enter a valid email address") });
type FormValues = z.infer<typeof schema>;

export function PasswordResetRequestPage() {
  const navigate = useNavigate();
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    // Deliberately unconditional - the backend never discloses whether the
    // email exists, and neither should this UI.
    await requestPasswordReset(values.email);
    setSubmitted(true);
  }

  return (
    <AuthShell title="Reset your password" subtitle="We'll email you a code if an account exists for that address.">
      {submitted ? (
        <div className="flex flex-col gap-4 text-center">
          <p className="text-sm text-ink-700">
            If that account exists, a reset code has been sent. Enter it on the next screen.
          </p>
          <Button size="sm"
          className="bg-black hover:bg-zinc-800 text-white"
          color="dark"
          onClick={() => navigate("/password-reset/confirm")}>Enter code</Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <Input label="Email" type="email" error={errors.email?.message} {...register("email")} />
          <Button type="submit" isLoading={isSubmitting}
          size="sm"
          className="bg-black hover:bg-zinc-800 text-white"
          color="dark"
          >
            Send reset code
          </Button>
        </form>
      )}
      <p className="mt-6 text-center text-sm text-ink-500">
        <Link to="/login" className="text-clinical-600 hover:underline">
          Back to sign in
        </Link>
      </p>
    </AuthShell>
  );
}
