from openai import OpenAI
from typing import Any
import os

from .prompt import SYSTEM_INSTRUCTIONS, PROMPT_TEMPLATE
from .parsing import main as parse_cot

from app.utils.exceptions import MissingParameterException
from app.utils.logging import get_logger


api_key=os.environ.get("API_KEY")

logger = get_logger("modules.CoT.main")

def run(payload: dict[str, Any]) -> str:
    job_id = payload.get("job_id", "N/A")
    logger.info("Running CoT module", extra={"job_id": job_id})

    try: 
        if "message" not in payload or not payload["message"]:
            logger.warning("No message provided in payload.", extra={"job_id": job_id})
            raise MissingParameterException("message")

        model = payload["model"] if "model" in payload else "gpt-5"
        api_key = payload["api_key"] if "api_key" in payload else os.environ.get("API_KEY")
        base_url = payload["base_url"] if "base_url" in payload else None
        temperature = payload["temperature"] if "temperature" in payload else 1
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": PROMPT_TEMPLATE.format(message=payload["message"])},
        ]
        
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages
        )
        logger.info("Received response from OpenAI API.", extra={"job_id": job_id})

        #parsed = parse_cot(response.choices[0].message.content)
        #print("Parsed CoT Output::", parsed)

        return {"response": response.choices[0].message.content}

    except Exception:
        logger.exception("Error occurred in CoT module", extra={"job_id": job_id})
        raise


