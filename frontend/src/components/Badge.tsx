export function Badge({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "healthy" | "mild" | "moderate" | "severe" | "info";
}) {
  const toneClasses: Record<string, string> = {
    neutral: "bg-ink-100 text-ink-700",
    healthy: "bg-severity-healthy/10 text-severity-healthy",
    mild: "bg-severity-mild/10 text-severity-mild",
    moderate: "bg-severity-moderate/10 text-severity-moderate",
    severe: "bg-severity-severe/10 text-severity-severe",
    info: "bg-clinical-100 text-clinical-800",
  };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${toneClasses[tone]}`}>
      {children}
    </span>
  );
}
