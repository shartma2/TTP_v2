from langchain.agents import create_agent

from modules.pipeline.schemes._generationPrompt import SYSTEM_INSTRUCTIONS
from app.models.PASSModel import PASSModel

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
        ).get("structured_response")

    return response