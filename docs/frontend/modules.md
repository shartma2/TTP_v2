# Frontend Modules

Frontend functionality is implemented as reusable module cards under `frontend/app/modules`.

All cards share the same visual shell (`ModuleCardSpec`) and are orchestrated by `app/page.tsx`.

---

## Shared card shell: `ModuleCardSpec`

`ModuleCardSpec` provides a consistent container for:

- title and description
- card body content
- optional footer area

This keeps style/layout consistency while allowing module-specific logic inside each card.

---

## Module cards

### `StandardModuleCard`

Used for direct message-based modules (`cot`, `pipeline`).

Behavior:

- collects free-text input
- queues job via `useJobRunner().run(module, { message })`
- notifies parent to refresh jobs after queueing

### `RefineModuleCard`

Used for refinement workflow.

Behavior:

- uses selected source job from sidebar
- fetches source job details (`/api/jobs/{sourceJobId}`)
- queues `refine` job with `{ source_job_id, message, result }`

### `ExportModuleCard`

Used to export a finished source job to `.json`, `.txt`, or `.owl`.

Behavior:

- selects export format
- queues `export` job with `{ source_job_id, format, result }`
- watches export job in job list
- creates downloadable `Blob` from returned base64 payload

### `ResultModuleCard`

Used to inspect a specific job result.

Behavior:

- loads selected/pasted job via `/api/jobs/{id}`
- shows status/errors for non-finished jobs
- renders result through `renderResult(...)`

### `JobsSidebar`

Operational control panel for all jobs.

Behavior:

- lists jobs sorted by latest update timestamp
- displays status badges (`queued`, `running`, `done`, `failed`)
- starts/stops polling for active jobs
- emits selected job id to parent

---

## Type contracts

`app/types.ts` defines the shared frontend model:

- `JobStatus`
- `Job`
- `ExportJobResult`
- `ExportFormat`

These types align UI assumptions with backend response shapes and reduce ad-hoc parsing in components.
