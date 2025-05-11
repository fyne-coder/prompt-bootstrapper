# Task: RankNode

## Objective
From the generated prompt groups, select the single best prompt in each group.

## Requirements
- Decorate with `@Node(retries=3)`.
- Input: `prompt_groups` (List[List[str]]), plus OpenAI parameters (`model`, `temperature`).
- Use the OpenAI Python 1.x client:
  ```python
  client = openai.OpenAI()
  resp = client.chat.completions.create(...)
  ```
- System prompt: you are a prompt ranking assistant.
- User prompt: provide the JSON-serialized prompt groups and request a JSON array of the best prompt per group.
- Parse the response with `json.loads`.
- Validate that the output is a list of strings, with the same length as the input groups.
- Retries up to 3 times on API/network errors.

## Acceptance Criteria
- Returns `List[str]` of length `len(prompt_groups)`, where each element is one of the original prompts.
- Raises `json.JSONDecodeError` if the API output is not valid JSON.
- Raises `ValueError` if the parsed JSON is not a list of the correct length or contains non-string items.