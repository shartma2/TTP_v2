# Configuration Overview

This project separates runtime configuration into environment files under `config/`.

---

## Frontend config

The frontend uses `config/frontend.env`.

Most important variable:

- `BACKEND_URL` → backend base URL used by Next.js API proxy routes (`frontend/app/api/jobs/*`)

Example (`config/frontend.env.example`):

```env
BACKEND_URL=http://backend:8000
```

With Docker Compose, `http://backend:8000` targets the backend service name on the internal network.

---

## Backend config 

The backend reads its own variables from `config/backend.env` (via `docker-compose.yaml`).

Most important variable:

- `API_KEY` → api key used for llm requests. Make sure to provide the correct key for the selected model (`frontend/app/api/jobs/*`)

Example (`config/frontend.env.example`):

```env
API_KEY=sk-proj-oJ...
```

Keep both real env files (`backend.env`, `frontend.env`) out of version control and maintain defaults in `*.env.example`.
