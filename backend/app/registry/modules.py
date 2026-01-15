from __future__ import annotations

from typing import Any, Callable


from modules.CoT.main import run_cot

ModuleFn = Callable[[dict[str, Any] | None], Any]

MODULES: dict[str, ModuleFn] = {
    "cot": run_cot,
}
