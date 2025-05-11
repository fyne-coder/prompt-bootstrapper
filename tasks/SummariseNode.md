# Task: SummariseNode

## Objective
Generate a concise master prompt (≤ 240 characters) summarising a business or webpage description.

## Requirements
- Decorate with `@Node(retries=3)`.
- Use the OpenAI ChatCompletion API:
  - Model: `gpt-3.5-turbo` (configurable via env).
  - System prompt: instruct the model to summarise for marketing prompts.
  - User prompt: include the raw text and request a ≤240-character summarisation.
  - Temperature: 0.7 (configurable).
- Extract the content from the first choice and trim to 240 characters.
- On API/network errors, retry up to 3 times before failing.

## Acceptance Criteria
- Given sample text, returns a string ≤ 240 characters.
- Trimming occurs if the model output exceeds 240 chars.
- Errors raised after 3 failed attempts.