from openai import OpenAI
from datetime import datetime
from typing import Any
import os

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
    temperature = payload["temperature"] if "temperature" in payload else 0.5
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
    print(f"[CoT][{ts}] Response: {response.choices[0].message.content}")
    print(f"[CoT][{ts}] finished with payload: {payload} ")
    return {"message": f"I am running the CoT module! I am carrying a heavy payload: {payload}"}
