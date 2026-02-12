from datetime import datetime
import json
from pathlib import Path
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
#from langchain.openai import ChatOpenAI
import os
from typing import Any
from app.utils.logging import get_logger

from ._prompt import SYSTEM_INSTRUCTIONS
from ._output import PASSModel

def run(message, model):
    agent = create_agent(
            model = model,
            tools = [],
            response_format = PASSModel
        )
    
    result = agent.invoke(
        {"messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": message},
            ]}
        )
    
    output = result["messages"][-1].content
    output_parsed: Any = output
    try:
        output_parsed = json.loads(output)
    except json.JSONDecodeError:
        pass
    return output_parsed