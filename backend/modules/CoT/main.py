from openai import OpenAI
from .prompt import build_prompt

client = OpenAI()

def run(payload) -> str:
    return f"I am running the CoT module! I am carrying a heavy payload: {payload}"
