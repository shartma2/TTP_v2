from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
import os
import pydantic
from typing import Any
from app.utils.logging import get_logger
from app.utils.logging import save_artifact
from app.utils.exceptions import MissingParameterException
from app.utils.exceptions import JobNotFoundException
from app.utils.exceptions import InvalidPASSModelException

from modules.refine.schemes._generationPrompt import SYSTEM_INSTRUCTIONS
from modules.refine.tools import build_tools

from modules.pipeline.schemes._output import PASSModel

api_key=os.environ.get("API_KEY")

logger = get_logger("modules.refine.main")

def run(payload: dict[str, Any]) -> dict[str, Any]:
    job_id = payload.get("job_id", "N/A")
    message = payload.get("message", None)
    source_job_id = payload.get("source_job_id", "N/A")
    source_job_content = payload.get("result", None)

    if not job_id:
        logger.warning("No job_id provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("job_id")
    if not source_job_id:
        logger.warning("No source_job_id provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("source_job_id")
    if not message:
        logger.warning("No message provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("message")
    if not source_job_content:
        logger.warning("No source_job_content provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("source_job_content")     

    status = source_job_content.get("status", None)

    if status != "done":
        logger.error("Job is not ready for export", extra={"job_id": job_id},)
        raise JobNotFoundException(f"Job is not ready for export: {source_job_id}")
    
    pass_model = source_job_content.get("result", {}).get("response")

    logger.info("Running Human-In-The-Loop module", extra={"job_id": job_id})


    tools = build_tools(pass_model)

    model = ChatOpenAI(
        model = payload.get("model", "gpt-5.2"),
        api_key = payload.get("api_key", api_key),
        base_url = payload.get("base_url", None),
        temperature = payload.get("temperature", 1),
    )

    agent = create_agent(
        model = model,
        tools = tools,
    )

    user_message = (
        "You are refining an existing PASS process model.\n\n"
        "Current PASS model:\n"
        f"{pass_model}\n\n"
        "User refinement request:\n"
        f"{message}\n\n"
        "Use tools whenever the request matches one of the supported structured operations. "
        "If the request cannot be fully handled with tools, do not guess additional tool calls."        
    )

    raw_response = agent.invoke(
        {
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": user_message},
            ]
        }
    )

    save_artifact(raw_response, job_id=job_id, prefix="ref")

    try:
        PASSModel.model_validate(pass_model)
    except:
        raise InvalidPASSModelException("Generated output is not a PASSModel.") 

    return pass_model