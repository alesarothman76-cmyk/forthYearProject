import { Link } from "react-router-dom";
import { SearchX } from "lucide-react";

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-24 text-center">
      <SearchX className="h-10 w-10 text-ink-300" />
      <p className="font-medium text-ink-900">Not found</p>
      <p className="text-sm text-ink-500">This record doesn't exist, or you don't have access to it.</p>
      <Link to="/" className="text-sm text-clinical-600 hover:underline">
        Go back
      </Link>
    </div>
  );
}
