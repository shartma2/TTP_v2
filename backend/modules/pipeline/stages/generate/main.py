from langchain.agents import create_agent
#from langchain.openai import ChatOpenAI
from typing import Any
import json

from modules.pipeline.schemes._prompt import SYSTEM_INSTRUCTIONS
from modules.pipeline.schemes._output import PASSModel

def run(message, model) -> PASSModel:
    agent = create_agent(
            model = model,
            tools = [],
            response_format = PASSModel
        )
    
    response = agent.invoke(
        {"messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": message},
            ]}
        )

    return response.get("structured_response")