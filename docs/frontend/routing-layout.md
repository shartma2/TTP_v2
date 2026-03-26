# Frontend Routing & Layout

The frontend uses the Next.js **App Router** with a compact route surface.

---

## Route structure

### UI routes

- `/` → main dashboard (`app/page.tsx`)

### Internal API routes (proxy)

- `/api/jobs` (`app/api/jobs/route.ts`)
	- `POST`: create backend jobs
	- `GET`: list jobs
- `/api/jobs/[id]` (`app/api/jobs/[id]/route.ts`)
	- `GET`: fetch single job details

These API routes are consumed by client components and forward to backend endpoints under `${BACKEND_URL}/api/jobs...`.

---

## Layout composition

### Root layout (`app/layout.tsx`)

The root layout defines global HTML/body structure, metadata, and font setup (`Geist`, `Geist Mono`).

### Dashboard page (`app/page.tsx`)

The main page composes a two-part layout:

- **left sidebar**: `JobsSidebar` (job list, polling-driven status updates)
- **content grid**: module cards (`StandardModuleCard`, `RefineModuleCard`, `ExportModuleCard`, `ResultModuleCard`)

On larger viewports, the sidebar is fixed and the module area offsets with a left margin. On smaller viewports, sidebar/content stack vertically.

---

## State ownership on the page

`app/page.tsx` is the state owner for:

- `jobs`
- loading/error state for job list
- currently selected job id

This state is passed down into sidebar/cards via props, which keeps inter-module coordination explicit and predictable.

---

## Navigation model

The current UI uses **in-page module switching** (card interactions + selected job state), not multi-page navigation.

That keeps workflow friction low for rapid iteration:

- queue a module run
- watch status in sidebar
- inspect/refine/export from the same screen
