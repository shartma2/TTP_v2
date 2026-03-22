# Module Registry

The registry provides a central mapping between **module identifiers** and their corresponding execution functions.

**File:** `app/registry/modules.py`

---

## Purpose

The registry defines which modules are available in the system and how they can be accessed at runtime.

It serves as a **lookup table** that allows other components (e.g., the service layer) to dynamically resolve and execute modules based on a string identifier.

---

## Structure

The registry is implemented as a simple dictionary:

```python
MODULES = {
    "cot": cot_run,
    "pipeline": pipeline_run,
    "export": export_run,
    "refine": refine_run,
    "rendering": rendering_run,
}
```

Each entry consists of:
- Key → Module name (string identifier used in requests)
- Value → Callable implementing the module logic