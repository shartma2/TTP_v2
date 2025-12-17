from openai import OpenAI
from .prompt import build_prompt

client = OpenAI()

def run() -> str:
    return "I am running the CoT module!"
