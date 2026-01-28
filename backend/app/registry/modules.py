from __future__ import annotations

from typing import Any, Callable


from modules.cot.main import run as run_cot
from modules.pipeline.main import run as run_pipeline

ModuleFn = Callable[[dict[str, Any] | None], Any]

MODULES: dict[str, ModuleFn] = {
    "cot": run_cot,
    "pipeline": run_pipeline,
}
