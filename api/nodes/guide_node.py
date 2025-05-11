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
def GuideNode(prompts: List[str],
              model: str = "gpt-3.5-turbo",
              temperature: float = 0.7) -> List[str]:
    """
    For each prompt, generate a usage tip (≤40 words), including model and temperature.
    """
    client = openai.OpenAI()
    system_msg = {
        "role": "system",
        "content": (
            "You are an AI usage guide. Generate a concise usage tip for each prompt provided."  
            " Each tip should be no more than 40 words and include recommended model and temperature settings."
        )
    }
    user_msg = {
        "role": "user",
        "content": (
            f"Prompts: {json.dumps(prompts)}\n"
            "Respond only with a JSON array of usage tips."
        )
    }
    resp = client.chat.completions.create(
        model=model,
        messages=[system_msg, user_msg],
        temperature=temperature,
    )
    try:
        content = resp.choices[0].message.content
    except Exception:
        content = resp["choices"][0]["message"]["content"]
    # Parse and validate JSON response
    tips = json.loads(content)
    if not isinstance(tips, list) or len(tips) != len(prompts):
        raise ValueError("Invalid number of usage tips returned")
    # Replace any empty or invalid tip with a fallback message
    default_tips = [
        f"Use the prompt '{p}' with model {model} and temperature {temperature}."
        for p in prompts
    ]
    for i, tip in enumerate(tips):
        if not isinstance(tip, str) or not tip.strip():
            tips[i] = default_tips[i]
    return tips