from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
#from langchain.openai import ChatOpenAI
from typing import Any
import json

from ._prompt import SYSTEM_INSTRUCTIONS
from ._output import PASSModel

def run(message, model) -> PASSModel:
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