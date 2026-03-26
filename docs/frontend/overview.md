# Frontend Overview

The frontend is a **Next.js App Router** application (`frontend/app`) that provides a unified UI for triggering backend modules and inspecting asynchronous job results.

Its core design principle is: keep browser code simple by routing all backend communication through internal Next.js API routes.

---

## Architecture at a glance

The frontend is organized into three main parts:

- **UI composition** in `app/page.tsx` (dashboard layout + module cards)
- **API proxy layer** in `app/api/jobs/*` (server-side forwarding to backend)
- **Reusable utilities** in `app/util/*` (job execution/polling and rendering helpers)

This gives a clean separation between view logic, network boundaries, and shared helper behavior.

---

## Runtime interaction with backend

The browser never calls the backend host directly.

Instead, UI components call local routes:

- `POST /api/jobs`
- `GET /api/jobs`
- `GET /api/jobs/{id}`

Those Next.js route handlers forward requests to `BACKEND_URL` (from environment config), preserving response status/body.

Benefits:

- stable same-origin API surface for the client
- no backend URL hardcoding in browser components
- deployment flexibility via environment variables

---

## Main user flow

1. User enters module input in one of the cards
2. Card queues a job through `useJobRunner().run(...)`
3. Jobs list refreshes and shows status (`queued`/`running`/`done`/`failed`)
4. Sidebar polling updates active jobs periodically
5. Result and export cards consume selected job data

The page acts as a module dashboard over a shared asynchronous job queue.

---

## Technology summary

- Next.js 16 App Router
- React 19 client components for interactive cards/sidebar
- TypeScript types in `app/types.ts`
- Tailwind-based styling in `app/globals.css`

---

## Design trade-offs

- **Strength:** low coupling between UI and backend host via proxy routes
- **Strength:** modular card-based feature extension in `app/modules`
- **Trade-off:** polling-based updates (simple/reliable) instead of real-time push
- **Trade-off:** single-page dashboard pattern; all modules share the same screen context
