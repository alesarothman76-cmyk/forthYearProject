# Alzheimer's MRI Diagnosis System — Frontend

A React + TypeScript SPA implementing the Doctor and Admin consoles
described in the project's frontend implementation plan (v2). Built
against the current backend (Django REST API) as it stands today —
synchronous MRI processing, no heatmap output yet — with the scan-status
observation logic deliberately written to require **no changes** once
the backend's async/Celery migration lands (see `features/mriScans/hooks.ts`).

## Setup

```bash
cp .env.example .env   # point VITE_API_BASE_URL at your backend
npm install
npm run dev
```

Requires the backend from the companion Django project running (default:
`http://localhost:8000/api`).

## Build

```bash
npm run build      # type-checks (tsc -b) then builds to dist/
npm run preview    # serve the production build locally
```

## Stack

React 18 (well, React 19 as installed) + TypeScript, Vite, React Router
v6, TanStack Query v5 (all server state), React Context (auth only),
react-hook-form + zod, axios, Tailwind CSS v4, Recharts, sonner (toasts),
lucide-react (icons).

## Design

Palette and typography were chosen deliberately against this project's
subject (a clinical neuroimaging tool) rather than defaulted: a
clinical teal/slate system (`tailwind.config.js`) instead of the generic
cream+terracotta or dark+neon looks default AI-assisted design tends
toward, IBM Plex Sans/Mono (self-hosted via `@fontsource`, no external
font CDN dependency — deliberate for a tool that may run in constrained
clinical network environments), and a single signature element (the
stylized signal-trace line in `AuthShell.tsx`) rather than decoration
scattered throughout. Severity badges use a consistent 4-color scale
(healthy → mild → moderate → severe) applied everywhere a
`DiseaseSeverity` value is shown, so the same color always means the
same thing across the whole app.

## What's implemented

- **Auth**: login, doctor self-registration, password reset
  (request/confirm — the same screen doubles as first-password setup for
  a newly-approved doctor), silent token refresh on load, role-gated
  routing (Doctor vs Admin), forced logout on refresh failure.
- **Patients**: list with search + gender/active/severity filters,
  create/edit (national ID immutable after creation, `current_status`
  never editable — it's system-derived), archive, detail page with the
  Phase 5 aggregated history timeline (scans + their reports in one view).
- **MRI Scans**: drag-and-drop upload with progress, status-aware detail
  page (queued/analyzing/completed/failed states, each written distinctly
  rather than a single generic spinner), class-probability chart,
  send-results-to-patient (disabled with an explanatory tooltip if the
  patient has no email on file; confirmation dialog states plainly that
  this is unencrypted email, not secure portal delivery).
- **Reports**: create from a completed scan, edit notes while draft
  (explicit Save button, not silent autosave), finalize (irreversible,
  stated as such in the confirm dialog), PDF download (authenticated
  blob fetch, not a plain `<a href>` — the endpoint requires a bearer
  token).
- **Admin**: approval queue (approve/reject with optional reason),
  doctor management (activate/deactivate/archive, filterable by
  registration status), read-only paginated patient oversight (no
  medical history shown, no edit/delete affordances anywhere on that
  screen — the backend has no such capability there, so the UI doesn't
  imply one exists).

## What's deliberately not implemented

- **Heatmap viewer** — `AIAnalysisResult.heatmap_image` is always `null`
  on the current backend. The result view renders cleanly around a null
  value (no broken image, no empty box) and simply omits the toggle;
  build the viewer once the field is confirmed populated.
- **Admin account management UI** — the backend enforces exactly one
  Admin account and rejects a second at the model layer; there is
  correspondingly no "add admin" screen anywhere in this app.
- **E2E test suite** (Playwright) — described in the frontend
  implementation plan but not yet written; this delivery is the
  application code itself.

## Known limitations worth flagging

- **No ESLint config** was scaffolded by this Vite version — `tsc -b`
  passes clean (zero type errors) and was used as the primary
  correctness gate for this delivery, but a lint pass would still be
  worth adding before this goes into a real CI pipeline.
- **Bundle size**: the production build is a single ~256 KB (gzipped)
  chunk. Fine for an internal tool at this scope; if the app grows,
  route-based code-splitting (`React.lazy` per top-level route) is the
  natural next step and wasn't done here to keep the initial delivery
  straightforward.
- **Refresh token in `localStorage`**: a stated tradeoff, not an
  oversight — see `src/api/tokenStore.ts`'s docstring and the frontend
  implementation plan's Section 4 for the reasoning.
