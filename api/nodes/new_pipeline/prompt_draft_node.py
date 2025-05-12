from api.nodes.fetch_summary_node import Node

@Node(retries=3)
def PromptDraftNode(text: str, framework_plan: dict) -> list[str]:
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
            "You are a prompt-drafting assistant.\n"
            "Return ONLY a pure JSON array (no markdown) containing **10-25** prompts.\n"
            "Each prompt MUST:\n"
            "• start with an imperative verb\n"
            f"• contain at least {min_phrases_required} distinct phrases from <key_phrases>\n"
            "• include explicit output constraints (format / length / schema)\n"
            "Prefix each prompt with a category tag: 'M:' (Marketing), 'Sa:' (Sales), "
            "'Su:' (Success), 'P:' (Product), or 'O:' (Ops)."
        ),
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
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1].strip()          # strip accidental fences

    try:
        prompts = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("PromptDraftNode JSON parse error: %s", raw)
        raise

    if not (isinstance(prompts, list) and 10 <= len(prompts) <= 25):
        raise ValueError(f"Expected 10-25 prompts, got {len(prompts)}")

    if any(not isinstance(p, str) or not p.strip() for p in prompts):
        raise ValueError("All prompts must be non-empty strings")

    return prompts