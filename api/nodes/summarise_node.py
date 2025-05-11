import functools

# OpenAI import with fallback stub
try:
    import openai
except ImportError:
    import types
    openai = types.SimpleNamespace()

# PocketFlow Node decorator stub with retry logic if pocketflow is unavailable
try:
    from pocketflow import Node
except ImportError:
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
        "content": (
            f"Summarise the following text into one marketing prompt (≤240 chars):\n{text}"
        ),
    }
    # Call OpenAI ChatCompletion
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[system_msg, user_msg],
        temperature=temperature,
    )
    # Extract content
    try:
        # new-style response
        content = resp.choices[0].message.content
    except Exception:
        # fallback for dict-like
        content = resp["choices"][0]["message"]["content"]
    # Trim to 240 chars
    return content.strip()[:240]