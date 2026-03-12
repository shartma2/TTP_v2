from __future__ import annotations

from langchain.agents import create_agent
from dataclasses import dataclass
from typing import List, Optional
import json

from modules.pipeline.schemes._output import PASSModel
from modules.pipeline.schemes._repairPrompt import SYSTEM_INSTRUCTIONS

@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    path: Optional[str] = None

def run(input: PASSModel, issues: List[Issue], model):
    agent = create_agent(
            model = model,
            tools = [],
            response_format = PASSModel
        )
    
    message = json.dumps({
        "model": input.model_dump(),
        "issues": [issue.__dict__ for issue in issues]
    }, indent=2)

    response = agent.invoke(
        {"messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": message},
            ]}
        ).get("structured_response")
    
    return response