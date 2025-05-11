import functools
import json
from typing import List

import openai

# Node decorator with retry logic
class Node:
    def __init__(self, retries: int = 0):
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
def RankNode(prompt_groups: List[List[str]],
             model: str = "gpt-3.5-turbo",
             temperature: float = 0.7) -> List[str]:
    """
    Select the best prompt from each group of prompts.
    Returns a list of best prompts, one per input group.
    """
    client = openai.OpenAI()
    # Prepare messages
    system_msg = {
        "role": "system",
        "content": (
            "You are a prompt ranking assistant."
            " For each group of prompts provided, select the single best prompt."
            " Return the result as a JSON array of strings."  
        )
    }
    user_msg = {
        "role": "user",
        "content": (
            f"Prompt groups: {json.dumps(prompt_groups)}"
            "\nProvide a JSON array with the best prompt from each group."
        )
    }
    resp = client.chat.completions.create(
        model=model,
        messages=[system_msg, user_msg],
        temperature=temperature,
    )
    # Extract content
    try:
        content = resp.choices[0].message.content
    except Exception:
        content = resp["choices"][0]["message"]["content"]
    # Parse JSON
    bests = json.loads(content)
    # Validate structure
    if not isinstance(bests, list) or len(bests) != len(prompt_groups):
        raise ValueError("Invalid output length from RankNode")
    for item in bests:
        if not isinstance(item, str):
            raise ValueError("Each best prompt must be a string")
    return bests