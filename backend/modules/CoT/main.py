from openai import OpenAI
from datetime import datetime
from typing import Any
import os
import json

from .prompt import SYSTEM_INSTRUCTIONS, PROMPT_TEMPLATE

api_key=os.environ.get("API_KEY")
base_url=""
model=""



def run(payload: dict[str, Any]) -> dict[str, Any]:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[CoT][{ts}] started with payload: {payload} ")
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
    
    # Prepare log payload with full response and request metadata
    try:
        resp_dict = response.model_dump()
    except Exception:
        try:
            resp_dict = response.__dict__
        except Exception:
            resp_dict = {"raw": str(response)}

    log_entry = {
        "timestamp": ts,
        "request": {
            "model": model,
            "temperature": temperature,
            "base_url": base_url,
            "api_key_present": bool(api_key),
        },
        "messages": messages,
        "response": resp_dict,
    }

    # Ensure container logs directory exists and write JSON log
    logs_dir = "/app/backend/logs"
    os.makedirs(logs_dir, exist_ok=True)
    log_filename = f"cot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path = os.path.join(logs_dir, log_filename)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)

    print(f"[CoT][{ts}] finished with payload: {payload} ")
    return {"response": response.choices[0].message.content}
