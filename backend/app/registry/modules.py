from __future__ import annotations

from typing import Any, Callable


from modules.cot.main import run as run_cot
from modules.pipeline.main import run as run_pipeline
from modules.export.main import run as run_export
from modules.refine.main import run as run_refine
from modules.rendering.main import run as run_rendering


ModuleFn = Callable[[dict[str, Any] | None], Any]

MODULES: dict[str, ModuleFn] = {
    "cot": run_cot,
    "pipeline": run_pipeline,
    "export": run_export,
    "refine": run_refine,
    "rendering": run_rendering
}
