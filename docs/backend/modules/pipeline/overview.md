# Pipeline Module Overview

The pipeline module transforms a natural-language process description into a validated `PASSModel`.

In contrast to single-step generation, this module executes a staged flow (`generate` → `validate` → optional `repair` → `validate`) and returns the resulting model to the job system.

---

## Integration in backend runtime

The pipeline is integrated through the standard backend execution stack:

1. Client submits `POST /api/jobs` with `module: "pipeline"`
2. API route delegates to `JobService.create_job(...)`
3. `JobService` resolves `"pipeline"` via `app/registry/modules.py`
4. `modules.pipeline.main.run(payload)` executes in background
5. Final `PASSModel` is stored in job result (`status: done`) or error is stored (`status: failed`)

This means pipeline execution is asynchronous and follows the same job lifecycle as all other modules.

---

## Pipeline orchestration (`modules/pipeline/main.py`)

The module-level `run(payload)` function is the orchestration entrypoint.

It performs:

- input checks (`job_id`, `message`)
- model client setup (`ChatOpenAI` with payload/env overrides)
- staged execution of generate/validate/repair
- artifact logging for generation and validation outputs
- strict type check that stage outputs are `PASSModel`

Pseudo-flow:

```text
run(payload)
	-> generate(message, model)
	-> save_artifact(prefix="gen")
	-> validate(model)
	-> if issues:
			 repair(model, issues, model)
			 validate(repaired_model)
			 if issues remain: warn
	-> return PASSModel
```

Important: the current implementation performs at most one repair cycle.

---

## Inputs and outputs

### Required payload fields

- `message`: natural-language process description
- `job_id`: injected by `JobService` (not normally provided by client)

### Optional payload fields

- `model`
- `api_key`
- `base_url`
- `temperature`

### Return type

`PASSModel` (`app/models/PASSModel.py`) with:

- `sid` (subjects + messages)
- `sbd` (subject behavior diagrams)

---

## Example job walkthrough

### 1) Create job

Request:

```http
POST /api/jobs
Content-Type: application/json

{
	"module": "pipeline",
	"payload": {
		"message": "A customer places an order. The shop confirms or rejects it...",
		"model": "gpt-5.2",
		"temperature": 0.7
	}
}
```

Response:

```json
{ "jobId": "6ec4e2d0-8fcb-4d7e-b8c2-8bc4c0bf3a59" }
```

### 2) Runtime execution

`JobService` stores job as `queued`, then `running`, and calls the registry function for `pipeline`.

Inside pipeline:

- `generate` creates an initial structured model
- `validate` returns issue list
- if issues exist, `repair` is invoked once
- `validate` runs again

Artifacts are written to `/app/backend/logs`:

- `gen_<job_id>.json` (generation result)
- `val_<job_id>.json` (validation issues, if any)

### 3) Poll job result

Request:

```http
GET /api/jobs/{job_id}
```

Typical success shape:

```json
{
	"jobId": "6ec4e2d0-8fcb-4d7e-b8c2-8bc4c0bf3a59",
	"status": "done",
	"module": "pipeline",
	"result": {
		"sid": { "subjects": [...], "messages": [...] },
		"sbd": [...]
	},
	"error": null,
	"created_at": "...",
	"started_at": "...",
	"finished_at": "..."
}
```

If generation/repair fails or output type is invalid, status becomes `failed` and `error` is populated.

---

## Operational notes

- Pipeline jobs are CPU/network bound and run under `JobService` concurrency limits
- Job records are in-memory only and are lost on backend restart
- Validation warnings after repair are logged; the final returned model is still provided
