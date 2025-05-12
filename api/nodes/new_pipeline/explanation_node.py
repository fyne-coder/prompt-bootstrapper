from api.nodes.fetch_summary_node import Node

@Node(retries=2)
def ExplanationNode(prompts: list[str]) -> list[str]:
    """
    Generate ≤40-word "When to use" tips for each prompt via LLM.
    Returns a list of tip strings matching prompts order.
    """
    import json
    import openai

    client = openai.OpenAI()
    system_msg = {
        "role": "system",
        "content": (
            "You are an AI usage guide. For each provided AI prompt, generate a concise 'When to use' tip in 40 words or less."
        )
    }
    user_msg = {
        "role": "user",
        "content": f"Prompts: {json.dumps(prompts)}\nRespond only with a JSON array of usage tips."
    }
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_msg, user_msg],
        temperature=0.7,
    )
    try:
        content = resp.choices[0].message.content
    except Exception:
        content = resp["choices"][0]["message"]["content"]
    # Clean up possible markdown or code fences
    raw = content.strip()
    if raw.startswith("```"):
        parts = raw.split('```')
        if len(parts) >= 3:
            raw = parts[1].strip()
    # Parse JSON output
    import logging
    logger = logging.getLogger(__name__)
    try:
        tips = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("ExplanationNode JSON parse error: %s", raw)
        raise
    if not isinstance(tips, list) or len(tips) != len(prompts):
        raise ValueError(f"Expected {len(prompts)} tips, got {len(tips) if isinstance(tips, list) else 'invalid'}")
    for tip in tips:
        if not isinstance(tip, str) or not tip.strip():
            raise ValueError("Each tip must be a non-empty string")
    return tips