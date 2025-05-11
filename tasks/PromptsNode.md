# Task: PromptsNode

## Objective
Generate 3–5 groups of 5 AI prompts each, based on a master prompt and brand color palette.

## Requirements
- Decorate with `@Node(retries=3)`.
- Input parameters:
  - `master_prompt` (str): the summary prompt from SummariseNode.
  - `palette` (List[str]): list of HEX color strings.
  - `model` (str): OpenAI model, default `gpt-3.5-turbo`.
  - `temperature` (float): sampling temperature, default 0.7.
- Use the OpenAI ChatCompletion API:
  - System prompt: instruct the model to act as a multi-group prompt generator.
  - User prompt: include master prompt and palette, request JSON array of prompt-groups.
  - Request 3–5 groups, each with exactly 5 prompts.
- Parse the ChatCompletion output as JSON (`json.loads`).
- Ensure the returned structure is a list of lists of strings.
- Retry up to 3 times on API/network errors.

## Acceptance Criteria
- Returns `List[List[str]]` with 3–5 groups, each list of 5 non-empty strings.
- Raises a JSON parsing error if the output is not valid JSON.
- Retries exactly 3 times on exceptions, then bubbles the last error.