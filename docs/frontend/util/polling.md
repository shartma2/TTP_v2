# Polling Utility

Job polling is implemented in `frontend/app/util/jobRunner.tsx` via the `useJobRunner()` hook.

The hook combines job creation and incremental status tracking for asynchronous backend jobs.

---

## Hook API

`useJobRunner()` exposes:

- `loading`, `jobId`
- `run(module, payload)`
- `setPollIds(ids)`
- `addPollIds(ids)`
- `startPolling(onUpdate, intervalMs)`
- `stopPolling()`

---

## Execution responsibilities

### Job creation

`run(module, payload)`:

- sends `POST /api/jobs`
- extracts and stores returned `jobId`
- prevents duplicate submits while loading

### Poll lifecycle

`startPolling(...)` performs periodic `GET /api/jobs/{id}` requests for tracked ids.

It:

- updates each job through callback (`onUpdate(job)`)
- removes terminal jobs from tracked set (`done`, `failed`)
- auto-stops when no active ids remain
- retries with backoff-like delay handling on polling errors

### Cleanup

Hook cleanup and `stopPolling()` clear pending timers to prevent stale background polling.

---

## Integration point

`JobsSidebar` owns polling orchestration in the UI:

- derives active ids from current `jobs` list (`queued`/`running`)
- calls `setPollIds(activeIds)`
- starts polling when needed, stops when no active jobs remain

This keeps polling policy centralized in one component while the hook handles mechanics.

---

## Why polling is used

- matches asynchronous backend job model well
- simple to operate and debug
- avoids additional websocket/SSE infrastructure

The current strategy favors implementation simplicity over real-time push complexity.
