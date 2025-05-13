from api.nodes.fetch_summary_node import Node

@Node(retries=3)
def PromptDraftNode(text: str, framework_plan: dict) -> dict[str, list[str]]:
    """
    Draft 10-25 raw prompts with explicit constraints and strong business anchoring.
    `framework_plan` **must** contain "key_phrases": list[str].
    """
    import json, hashlib, logging, openai

    logger = logging.getLogger(__name__)
    key_phrases: list[str] = framework_plan.get("key_phrases", [])
    min_phrases_required = 2 if key_phrases else 1        # fallback if none

    client = openai.OpenAI()

    system_msg = {
        "role": "system",
        "content": (
            "Draft 10-25 AI prompts grouped by business function. "
            "Return ONLY valid JSON shaped as:\n"
            "{\n"
            "  \"Marketing\": [\"You are a ...\", ...],\n"
            "  \"Sales\": [...],\n"
            "  \"Success\": [...],\n"
            "  \"Product\": [...],\n"
            "  \"Ops\": [...]\n"
            "}\n"
            f"Rules: • each prompt begins with \"You are a ...\" • min {min_phrases_required} key-phrases "
            "• ≤220 tokens • quotas: Marketing 3, Sales 2, Success 2, Product 2, Ops 1."
        )
    }

    user_msg = {
        "role": "user",
        "content": (
            f"<business_text>{text}</business_text>\n"
            f"<key_phrases>{', '.join(key_phrases)}</key_phrases>\n"
            f"<framework_plan>{json.dumps(framework_plan, ensure_ascii=False)}</framework_plan>"
        ),
    }

    seed_val = int(
        hashlib.sha256((text + 'gpt-4.1-mini-2025-04-14').encode()).hexdigest(), 16
    ) % 2**31

    resp = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14",
        messages=[system_msg, user_msg],
        temperature=0.0,          # deterministic
        seed=seed_val,
    )

    raw = resp.choices[0].message.content.strip()
    # Strip code fences and extract JSON object
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) >= 3:
            raw = parts[1].strip()
    # Extract first JSON object
    obj_start = raw.find('{')
    obj_end = raw.rfind('}')
    if obj_start != -1 and obj_end != -1:
        raw = raw[obj_start:obj_end+1]
    try:
        prompts_by_cat = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("PromptDraftNode JSON parse error: %s", raw)
        raise

    if not isinstance(prompts_by_cat, dict):
        raise ValueError("Expected JSON object mapping categories to lists of prompts")

    # Silently allow categories with fewer than quotas; list integrity check
    for cat, items in prompts_by_cat.items():
        if not isinstance(items, list) or any(not isinstance(p, str) or not p.strip() for p in items):
            raise ValueError(f"Invalid prompts list for category '{cat}'")

    return prompts_by_cat