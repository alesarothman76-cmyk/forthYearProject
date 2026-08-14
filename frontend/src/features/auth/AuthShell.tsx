import type { ReactNode } from "react";
import { Activity } from "lucide-react";

/**
 * Design note: a clinical dashboard is a working tool, not a marketing
 * surface, so the bulk of this app is deliberately quiet - the one place
 * worth a distinct visual signature is this shared entry point, since
 * every user sees it first. Signature element: a thin horizontal "signal
 * trace" rule (a stylized EEG/pulse line) under the wordmark, rendered in
 * the clinical teal, in place of a generic logo mark - a nod to the
 * subject (neurological signal analysis) without literal iconography.
 */
export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-3">
          <div className="flex items-center gap-2 text-ink-900">
            <Activity className="h-5 w-5 text-clinical-600" strokeWidth={2.25} />
            <span className="font-mono text-sm font-medium tracking-wide">NEUROSCAN CLINICAL</span>
          </div>
          <svg width="220" height="10" viewBox="0 0 220 10" className="text-clinical-400" aria-hidden="true">
            <polyline
              points="0,5 60,5 72,1 84,9 96,5 220,5"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div className="rounded-lg border border-ink-100 bg-white p-7 shadow-sm">
          <h1 className="text-lg font-semibold text-ink-900">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-ink-500">{subtitle}</p>}
          <div className="mt-6">{children}</div>
        </div>
      </div>
    </div>
  );
}
