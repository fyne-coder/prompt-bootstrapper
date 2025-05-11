import functools

import openai

# Node decorator with retry logic
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
            if last_exc:
                raise last_exc
            return fn(*args, **kwargs)

        wrapper.__wrapped__ = fn
        return wrapper

@Node(retries=3)
def SummariseNode(text: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> str:
    """
    Summarise the input text into a single marketing prompt of up to 240 characters.
    Retries up to `retries` times on API or network errors.
    """
    # Initialize OpenAI client
    client = openai.OpenAI()
    # Prepare messages
    system_msg = {
        "role": "system",
        "content": (
            "You are a concise summarisation assistant."
            " Given raw business or webpage text, produce a single marketing prompt"
            " that captures the core positioning in no more than 240 characters."
        ),
    }
    user_msg = {
        "role": "user",
        "content": f"Summarise the following text into one marketing prompt (≤240 chars):\n{text}",
    }
    # Call OpenAI ChatCompletion via new client interface
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
    return content.strip()[:240]