from time import sleep
from openai import OpenAI
from .prompt import build_prompt
from datetime import datetime

client = OpenAI()

def run(payload) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[CoT][{ts}] started with payload: {payload} ")
    sleep(5) 
    print(f"[CoT][{ts}] finished with payload: {payload} ")
    return f"I am running the CoT module! I am carrying a heavy payload: {payload}"
