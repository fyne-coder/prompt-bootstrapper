# Task: GuideNode

## Objective
Generate concise usage tips (≤40 words) for a list of best prompts, including recommended model and temperature settings.

## Requirements
- Decorate with `@Node(retries=3)`.
- Input:
  - `prompts` (List[str]): best prompts per group.
  - `model` (str): default `gpt-3.5-turbo`.
  - `temperature` (float): default `0.7`.
- Use OpenAI Python client:
  ```python
  client = openai.OpenAI()
  resp = client.chat.completions.create(...)
  ```
- System prompt: instruct to produce usage tips ≤40 words.
- User prompt: provide JSON list of prompts, request JSON array of corresponding usage tips.
- Parse with `json.loads`.
- Validate the result is a list of strings with same length as input.
- Retries up to 3 times on errors.

## Acceptance Criteria
- Returns `List[str]` of usage tips, length == len(prompts).
- Each tip is a non-empty string.
- Raises `json.JSONDecodeError` for invalid JSON.
- Raises `ValueError` for wrong structure or length.