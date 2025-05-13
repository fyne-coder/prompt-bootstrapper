import logging
import json
from api.nodes.fetch_summary_node import Node
from api.config import OPENAI_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prompt quotas per category (total 9 slots)
QUOTAS = {"Marketing": 3, "Sales": 2, "Product": 2, "Success": 1, "Ops": 1}

@Node(retries=3)
def PromptDraftNode(text: str, framework_plan: dict) -> dict[str, list[str]]:
    """
    Draft 10-25 raw prompts with explicit constraints and strong business anchoring.
    `framework_plan` **must** contain "key_phrases": list[str].
    """
    import openai, hashlib

    # Framework plan may include quotas and capsule context
    client = openai.OpenAI()

    # System prompt for generating prompt packs grounded in business capsule
    system_msg = {
        "role": "system",
        "content": (
            "You are a Prompt-Pack Generator. Given a Business Context Capsule and a framework plan, "
            "generate 10–25 high-quality prompts grouped by business function. "
            "Return ONLY valid JSON mapping categories to arrays of prompt strings. "
            "Prompts must be no more than 220 tokens each. "
            f"Quotas per category: {QUOTAS}."
        )
    }

    user_msg = {
        "role": "user",
        "content": (
            f"<capsule>{text}</capsule>\n"
            f"<framework_plan>{json.dumps(framework_plan, ensure_ascii=False)}</framework_plan>"
        ),
    }

    # Use deterministic seed for repeatability
    seed_val = int(
        hashlib.sha256((text + OPENAI_MODEL).encode()).hexdigest(), 16
    ) % 2**31

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[system_msg, user_msg],
        temperature=0.35,
        seed=seed_val,
    )

    raw = resp.choices[0].message.content.strip()
    logger.info("PromptDraftNode raw LLM output: %s", raw[:1000])
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
        logger.info("PromptDraftNode parsed JSON: %r", prompts_by_cat)
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