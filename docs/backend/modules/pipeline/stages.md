# Pipeline Stages

The pipeline is implemented as three explicit stages under `modules/pipeline/stages`:

- `generate`
- `validate`
- `repair`

The orchestration in `modules/pipeline/main.py` composes these stages into one module-level execution flow.

---

## Stage 1: Generate (`stages/generate/main.py`)

### Purpose

Create an initial structured `PASSModel` from natural-language input.

### Implementation

- uses `langchain.agents.create_agent(...)`
- configures `response_format=PASSModel` to enforce structured output
- sends generation system prompt (`schemes/_generationPrompt.py`) and user message

### Input / output

- Input: `message: str`, `model` (configured `ChatOpenAI` instance)
- Output: `PASSModel`

This stage performs no semantic rule checking; it focuses on first-pass model synthesis.

---

## Stage 2: Validate (`stages/validate/main.py`)

### Purpose

Apply deterministic rule checks to the generated model.

### Output type

Returns `List[Issue]` where each issue contains:

- `code`
- `message`
- optional `path`

### Validation groups

The validator aggregates issues from five rule groups:

1. `_validate_sid`  
	Checks subject labels, duplicate subjects, sender/receiver consistency, message presence.

2. `_validate_sbds`  
	Checks SBD subject coverage, duplicate SBD subjects, duplicate states, transition source/target validity.

3. `_validate_transitions`  
	Enforces transition-specific constraints:
	- `DoTransition` must not carry message/partner
	- communication transitions require `message` and `partner`

4. `_cross_check_messages`  
	Ensures `SendTransition` / `ReceiveTransition` are declared in SID message triples.

5. `_validate_start_end`  
	Enforces exactly one start state per SBD and no outgoing transitions from end states.

This stage is purely rule-based and model-local (no external calls).

---

## Stage 3: Repair (`stages/repair/main.py`)

### Purpose

Repair an invalid model using the issue list produced by validation.

### Implementation

- builds an LLM agent with `response_format=PASSModel`
- serializes current model + issue list into a JSON user message
- applies repair system prompt (`schemes/_repairPrompt.py`)

### Input / output

- Input: `pass_model: PASSModel`, `issues: List[Issue]`, `model`
- Output: repaired `PASSModel`

The contract is minimal-change repair: fix reported rule violations while preserving correct parts.

---

## Stage composition semantics

`pipeline/main.py` uses these stages with the following semantics:

- generate once
- validate
- if issues exist: repair once
- validate again
- return resulting model

If issues remain after the second validation, a warning is logged (no additional repair loop is executed in current implementation).

---

## Error and type boundaries

- Pipeline orchestration requires `job_id` and `message`, otherwise raises `MissingParameterException`
- Stage outputs are checked via `_check_pass_model(...)`; invalid output raises `InvalidPASSModelException`
- Exceptions propagate to `JobService`, which marks the job as `failed`

This separates deterministic validation errors (as issue list) from hard execution failures (exceptions).

---

## Example stage-level trace

For a single pipeline job, a typical trace is:

1. `generate` returns initial model
2. `validate` returns e.g. `SEND_NOT_IN_SID`, `START_STATE_COUNT`
3. `repair` receives original model + issues and returns updated model
4. `validate` reruns; issues list becomes empty
5. pipeline returns repaired `PASSModel`

If step 4 still returns issues, job may still complete with `done`, but unresolved issues are logged as warnings.
