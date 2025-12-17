SYSTEM_INSTRUCTIONS = """You are a funny guy or girl. Tell funny jokes about my topic."""

def build_prompt(user_input: str) -> dict:
    """
    Returns a dict with 'instructions' and 'input' so the caller can send it to the LLM.
    """
    return {
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": user_input.strip(),
    }
