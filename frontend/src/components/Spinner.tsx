import { Loader2 } from "lucide-react";

export function Spinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const px = size === "sm" ? "h-4 w-4" : size === "lg" ? "h-8 w-8" : "h-5 w-5";
  return <Loader2 className={`animate-spin text-clinical-500 ${px}`} aria-label="Loading" />;
}
