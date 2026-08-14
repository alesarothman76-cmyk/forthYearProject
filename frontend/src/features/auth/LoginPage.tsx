import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../app/AuthContext";
import { Button } from "../../components/Button";
import { Input } from "../../components/Input";
import { ErrorBanner } from "../../components/ErrorBanner";
import { AuthShell } from "./AuthShell";
import type { ApiError } from "../../api/types";

const schema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});
type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await login(values.username, values.password);
    } catch (err) {
      const apiError = err as ApiError;
      setError(
        apiError.status_code === 401
          ? "Incorrect username or password, or this account is not yet active."
          : apiError.detail
      );
      return;
    }
  }

  // Redirect after a successful login (user state updates asynchronously).
  useEffect(() => {
    if (!user) return;
    const from = (location.state as { from?: Location })?.from;
    navigate(from?.pathname ?? (user.role === "ADMIN" ? "/admin" : "/patients"), { replace: true });
  }, [user, location.state, navigate]);

  return (
    <AuthShell title="Sign in" subtitle="Access your patient records and analyses.">
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        {error && <ErrorBanner message={error} />}
        <Input label="Username" autoComplete="username" error={errors.username?.message} {...register("username")} />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <Button type="submit" isLoading={isSubmitting} className="mt-2 w-full bg-black hover:bg-zinc-800 text-white" color="dark">
        Sign in
        </Button>
      </form>
      <div className="mt-6 flex flex-col gap-1 text-center text-sm text-ink-500">
        <Link to="/password-reset/request" className="text-clinical-600 hover:underline">
          Forgot your password?
        </Link>
        <span>
          New doctor?{" "}
          <Link to="/register" className="text-clinical-600 hover:underline">
            Request an account
          </Link>
        </span>
      </div>
    </AuthShell>
  );
}
