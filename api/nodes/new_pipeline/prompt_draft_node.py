from api.nodes.fetch_summary_node import Node

@Node(retries=3)
def PromptDraftNode(text: str, framework_plan: dict) -> list[str]:
    """
    Use LLM to draft 15-25 raw prompts based on cleaned text and framework plan.
    Returns a list of prompt strings.
    """
    import json
    import openai

    # Initialize OpenAI client
    client = openai.OpenAI()
    # System message: instruct to draft raw prompts
    system_msg = {
        "role": "system",
        "content": (
            "You are a prompt drafting assistant. Generate between 15 and 25 distinct AI prompts "
            "based on the following business text and framework plan. Each prompt should start with an imperative verb, "
            "reference at least one key business term, and be no more than 220 tokens. "
            "Respond only with a JSON array of prompt strings."
        ),
    }
    # User message: provide text and plan
    user_msg = {
        "role": "user",
        "content": (
            f"Business text:\n{text}\n"
            f"Framework plan: {json.dumps(framework_plan)}"
        ),
    }
    # Call chat completion
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_msg, user_msg],
        temperature=0.7,
    )
    # Extract content
    try:
        content = resp.choices[0].message.content
    except Exception:
        content = resp["choices"][0]["message"]["content"]
    # Set up logger
    import logging
    logger = logging.getLogger(__name__)
    # Clean up possible markdown or code fences
    raw = content.strip()
    if raw.startswith("```"):
        # Remove fencing
        # drop first fence line
        parts = raw.split('```')
        # parts: ['', 'json\n[...]', ''] or ['', '', '[...]', '']
        # take the middle part
        if len(parts) >= 3:
            raw = parts[1].strip()
    # Parse JSON
    # Parse JSON output
    try:
        prompts = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("PromptDraftNode JSON parse error: %s", raw)
        raise
    # Validate list of strings
    if not isinstance(prompts, list):
        raise ValueError("Invalid prompts format: expected list of strings")
    # Validate count
    if not (15 <= len(prompts) <= 25):
        raise ValueError(f"Expected 15-25 prompts, got {len(prompts)}")
    # Validate each prompt
    for p in prompts:
        if not isinstance(p, str) or not p.strip():
            raise ValueError("Each prompt must be a non-empty string")
    return prompts