import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";

export function ForbiddenPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-3 bg-canvas text-center">
      <ShieldAlert className="h-10 w-10 text-ink-300" />
      <p className="font-medium text-ink-900">You don't have access to this page</p>
      <Link to="/login" className="text-sm text-clinical-600 hover:underline">
        Back to sign in
      </Link>
    </div>
  );
}
