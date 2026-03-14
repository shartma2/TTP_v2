from __future__ import annotations

from langchain.agents import create_agent
from dataclasses import asdict
from typing import List, Optional
import json

from modules.pipeline.schemes._output import PASSModel
from modules.pipeline.schemes._repairPrompt import SYSTEM_INSTRUCTIONS
from modules.pipeline.stages.validate.main import Issue

def run(pass_model: PASSModel, issues: List[Issue], model):
    agent = create_agent(
            model = model,
            tools = [],
            response_format = PASSModel
        )
    
    message = json.dumps({
        "model": pass_model.model_dump(),
        "issues": [asdict(issue) for issue in issues]
    }, indent=2)

    response = agent.invoke(
        {"messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": message},
            ]}
        ).get("structured_response")
    
    return response