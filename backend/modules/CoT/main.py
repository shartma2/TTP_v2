from openai import OpenAI
from typing import Any
import os
from backend.modules.logging.main import log

from .prompt import SYSTEM_INSTRUCTIONS, PROMPT_TEMPLATE

api_key=os.environ.get("API_KEY")
base_url=""
model=""



def run(payload: dict[str, Any]) -> dict[str, Any]:
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

    log(response, "cot", model, temperature, base_url, api_key, messages)

    return {"response": response.choices[0].message.content}
