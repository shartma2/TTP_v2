from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
#from langchain.openai import ChatOpenAI
import os
from typing import Any
from app.utils.logging import get_logger

from ._prompt import PROMPT
from ._weather import getWeather

api_key=os.environ.get("API_KEY")


logger = get_logger("modules.pipeline.main")


def run(payload: dict[str, Any]) -> dict[str, Any]:
    job_id = payload.get("job_id", "N/A")
    logger.info("Running Pipeline module", extra={"job_id": job_id})
    # llm = ChatOpenAI(
    #     model = payload["model"] if "model" in payload else "gpt-5",
    #     api_key = payload["api_key"] if "api_key" in payload else os.environ.get("API_KEY"),
    #     base_url = payload["base_url"] if "base_url" in payload else None,
    #     temperature = payload["temperature"] if "temperature" in payload else 1,
    # )

    try: 
        if "message" not in payload or not payload["message"]:
            logger.warning("No message provided in payload.", extra={"job_id": job_id})
            return {"error": "No message provided in payload."}
    
        model = ChatOpenAI(
        model = payload["model"] if "model" in payload else "gpt-5.2",
        api_key = payload["api_key"] if "api_key" in payload else os.environ.get("API_KEY"),
        base_url = payload["base_url"] if "base_url" in payload else None,
        temperature = payload["temperature"] if "temperature" in payload else 1,
        )
            
        agent = create_agent(
            model = model,
            tools = [getWeather],
        )

        result = agent.invoke(
        {"messages": [{"role": "user", "content": payload["message"]}]}
        )
        logger.info("Received response from Langchain Agent.", extra={"job_id": job_id})
        output = result["messages"][-1].content
        return {"response": output}


    except Exception:
        logger.exception("Error occurred in Pipeline module", extra={"job_id": job_id})
        return {"error": "An error occurred while processing the request."}
    