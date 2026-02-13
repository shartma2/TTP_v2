from langchain_openai import ChatOpenAI
#from langchain.openai import ChatOpenAI
import os
from typing import Any
from app.utils.logging import get_logger
from app.utils.logging import save_artifact
from app.utils.errors import MissingMessageError
from .stages.generate.main import run as generate

api_key=os.environ.get("API_KEY")



logger = get_logger("modules.pipeline.main")


def run(payload: dict[str, Any]) -> dict[str, Any]:
    job_id = payload.get("job_id", "N/A")
    message = payload.get("message", None)
    logger.info("Running Pipeline module", extra={"job_id": job_id})

    try: 
        if "message" not in payload or not message:
            logger.warning("No message provided in payload.", extra={"job_id": job_id})
            raise MissingMessageError("No message provided in payload")
    
        model = ChatOpenAI(
        model = payload["model"] if "model" in payload else "gpt-5.2",
        api_key = payload["api_key"] if "api_key" in payload else api_key,
        base_url = payload["base_url"] if "base_url" in payload else None,
        temperature = payload["temperature"] if "temperature" in payload else 1,
        )
        
        response = generate(message, model)
        logger.info("Received response from Langchain Agent.", extra={"job_id": job_id})

        save_artifact(job_id, payload.get("message"), response)
        logger.info("Saved minimal run artifact", extra={"job_id": job_id})

        return {"response": response}

    except MissingMessageError as e:
        raise

    except Exception:
        logger.exception("Error occurred in Pipeline module", extra={"job_id": job_id})
        return {"error": "An error occurred while processing the request."}
    