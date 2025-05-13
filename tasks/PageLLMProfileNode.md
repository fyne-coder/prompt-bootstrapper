# Task: PageLLMProfileNode

## Objective
Use a single LLM call (with built-in web_search) to profile a business homepage.
Extract and return JSON fields:
  - name: string
  - sector: string
  - services: list[str] (≤5)
  - geo: string
  - value_props: list[str] (3–5)
  - brand_tone: string (one of ['friendly','formal','premium','fun','neutral','playful'])
  - keywords: list[str] (≤8)

## Requirements
- Decorate with `@Node(retries=2)` and cache with `@lru_cache(maxsize=128)`.
- Use `openai.OpenAI().chat.completions.create` with:
  - `model=OPENAI_MODEL`
  - `tools=[{"type":"web_search"}]`
  - `response_format={"type":"json_object"}`
  - `temperature=0.3`, `max_tokens=400`
  - messages: a system instruction and user URL with `"tool":"web_search"`.
- If the LLM call fails, raise; if JSON parse fails, log and default to empty fields.

## Output
Returns a dict with exactly the seven keys above, defaulting to empty string or empty list.

## Test Acceptance
- Mock the OpenAI client to return a known JSON string.
- Assert `PageLLMProfileNode(url)` returns a dict with correct keys and defaults.