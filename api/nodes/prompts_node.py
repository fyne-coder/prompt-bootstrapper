import functools
import json
from typing import List

# OpenAI import
try:
    import openai
except ImportError:
    openai = None

# Node decorator (retry stub if PocketFlow not present)
class Node:
    def __init__(self, retries=0):
        self.retries = retries

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for _ in range(self.retries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
            if last_exc is not None:
                raise last_exc
            return fn(*args, **kwargs)
        wrapper.__wrapped__ = fn
        return wrapper

@Node(retries=3)
def PromptsNode(master_prompt: str,
                palette: List[str],
                model: str = "gpt-3.5-turbo",
                temperature: float = 0.7) -> List[List[str]]:
    """
    Generate 3-5 groups of 5 prompts each, returning a list of prompt lists.
    """
    if openai is None:
        raise RuntimeError("OpenAI SDK not available")
    system_msg = {
        "role": "system",
        "content": (
            "You are a prompt generator. Create 3 to 5 groups,"
            " each containing exactly 5 AI prompts, for a user-provided master prompt"
            " and brand color palette. Return the result as a JSON array of arrays."
        )
    }
    user_msg = {
        "role": "user",
        "content": (
            f"Master prompt: {master_prompt}\n"
            f"Color palette: {palette}\n"
            "Respond only with valid JSON: array of prompt groups."
        )
    }
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[system_msg, user_msg],
        temperature=temperature,
    )
    # Extract the content
    try:
        content = resp.choices[0].message.content
    except Exception:
        content = resp["choices"][0]["message"]["content"]
    # Parse as JSON
    prompts = json.loads(content)
    # Validate structure
    if not isinstance(prompts, list) or not all(isinstance(group, list) for group in prompts):
        raise ValueError("Invalid prompts format, expected list of lists")
    return prompts