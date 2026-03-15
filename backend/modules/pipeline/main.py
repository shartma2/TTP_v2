from langchain_openai import ChatOpenAI
import os
from typing import Any

from app.utils.logging import get_logger
from app.utils.logging import save_artifact
from app.utils.exceptions import MissingParameterException
from app.utils.exceptions import InvalidPASSModelException
from modules.pipeline.stages.generate.main import run as generate
from modules.pipeline.stages.validate.main import run as validate, Issue
from modules.pipeline.stages.repair.main import run as repair
from .schemes._output import PASSModel

api_key=os.environ.get("API_KEY")
logger = get_logger("modules.pipeline.main")

def run(payload: dict[str, Any]) -> PASSModel:
    job_id = payload.get("job_id", None)
    message = payload.get("message", None)
    logger.info("Running Pipeline module", extra={"job_id": job_id})

    if not job_id:
        logger.warning("No job_id provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("job_id")
    if not message:
        logger.warning("No message provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("message")

    model = ChatOpenAI(
        model = payload.get("model", "gpt-5.2"),
        api_key = payload.get("api_key", api_key),
        base_url = payload.get("base_url", None),
        temperature = payload.get("temperature", 1),
    )
    
    response = generate(message, model)
    
    logger.info("Received response from Langchain Agent.", extra={"job_id": job_id})
    save_artifact(input= payload.get("message"), output= response, job_id = job_id, prefix="gen")

    response = check_pass_model(response)
    issues = validate_and_log(response, job_id)
    if issues:
        response = repair(response, issues, model)
        response = check_pass_model(response)
        issues = validate_and_log(response, job_id)
        if issues:
            logger.warning("Validation issues remain after repair attempt.", extra={"job_id": job_id})

    return {"response": response}
    
def check_pass_model(response: object) -> PASSModel:
    if(not isinstance(response, PASSModel)):
        raise InvalidPASSModelException("Generated output is not a PASSModel.")
    return response

def validate_and_log(response: PASSModel, job_id: str) -> list[Issue]:
    issues = validate(response)
    if issues:
        save_artifact(output=issues, job_id=job_id, prefix="val")
        logger.warning(
            "Validation completed. Issues were found and saved to artifact",
            extra={"job_id": job_id},
        )
    else:
        logger.info(
            "Validation completed. No issues found.",
            extra={"job_id": job_id},
        )

    return issues
