from langchain_openai import ChatOpenAI
import os
from typing import Any
from app.utils.logging import get_logger
from app.utils.logging import save_artifact
from app.utils.exceptions import MissingMessageException
from app.utils.exceptions import InvalidPASSModelException
from modules.pipeline.stages.generate.main import run as generate
from modules.pipeline.stages.validate.main import run as validate

from .schemes._output import PASSModel

api_key=os.environ.get("API_KEY")



logger = get_logger("modules.pipeline.main")


def run(payload: dict[str, Any]) -> dict[str, Any]:
    job_id = payload.get("job_id", "N/A")
    message = payload.get("message", None)
    logger.info("Running Pipeline module", extra={"job_id": job_id})

    try: 
        if "message" not in payload or not message:
            logger.warning("No message provided in payload.", extra={"job_id": job_id})
            raise MissingMessageException("No message provided in payload")
    
        model = ChatOpenAI(
        model = payload.get("model", "gpt-5.2"),
        api_key = payload.get("api_key", api_key),
        base_url = payload.get("base_url", None),
        temperature = payload.get("temperature", 1),
        )
        
        response = generate(message, model)
        logger.info("Received response from Langchain Agent.", extra={"job_id": job_id})

        save_artifact(input= payload.get("message"), output= response, job_id = job_id, prefix="gen")
        logger.info("Saved minimal run artifact", extra={"job_id": job_id})

        if(not isinstance(response, PASSModel)):
            raise InvalidPASSModelException("Generated output is not a PASSModel.")

        issues = validate(response)
        if issues:
            save_artifact(output=issues, job_id=job_id, prefix="val")
            logger.warning("Validation completed. Issues were found and saved to artifact", extra={"job_id":job_id})

        else: 
            logger.info("Validation completed. No issues found.", extra={"job_id":job_id})

        return {"response": response}

    except MissingMessageException:
        raise

    except InvalidPASSModelException:
        raise

    except Exception:
        logger.exception("Error occurred in Pipeline module", extra={"job_id": job_id})
        raise
    