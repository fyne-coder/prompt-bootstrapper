import logging
import json
import hashlib
from api.nodes.fetch_summary_node import Node
from api.config import OPENAI_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prompt quotas per category (for reference)
QUOTAS = {"Marketing": 3, "Sales": 2, "Product": 2, "Success": 1, "Ops": 1}

@Node(retries=3)
def PromptDraftNode(text: str, framework_plan: dict) -> dict[str, list[str]]:
    """
    Draft 10–25 structured prompts, then return them grouped by category.
    """

    import openai

    client = openai.OpenAI()

    system_content = """
You are Prompt-Pack Generator v2.
Given a Business Context Capsule and a framework plan, your task is to generate 10–25 high-quality AI shortcuts grouped by business function.

# Framework options
RTF    = Role ▸ Task ▸ Format
RISEN  = Role ▸ Input ▸ Steps ▸ Expected ▸ Narrowing
CRISPE = Capacity ▸ Insight ▸ Statement ▸ Personality ▸ Experiment
RTC3   = Role ▸ Task ▸ Context ▸ Constraints ▸ Criteria

# Instructions
• Use the capsule to anchor each prompt.
• Pick the best framework for each category slot.
• Keep each prompt under ~280 tokens.
• Return ONLY valid JSON: an array of objects:
  [
    {
      "category": "Marketing",
      "framework": "CRISPE",
      "prompt_lines": [
         "Capacity: …",
         "Insight: …",
         …
      ]
    },
    …
  ]
• No extra commentary or markdown fences.
"""
    system_msg = {"role": "system", "content": system_content}

    user_content = (
        f"<capsule>{text}</capsule>\n"
        f"<framework_plan>{json.dumps(framework_plan, ensure_ascii=False)}</framework_plan>"
    )
    user_msg = {"role": "user", "content": user_content}

    # seed for determinism
    seed_val = int(
        hashlib.sha256((text + OPENAI_MODEL).encode()).hexdigest(), 16
    ) % (2**31)

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[system_msg, user_msg],
        temperature=0.7,
        max_tokens=1500,
        seed=seed_val,
    )

    raw = resp.choices[0].message.content.strip()
    logger.info("Raw LLM output: %s", raw[:500])
    # Legacy fallback: if the LLM returned a plain dict of category→list[str], return it directly
    try:
        parsed0 = json.loads(raw)
        if isinstance(parsed0, dict) and all(
            isinstance(v, list) and all(isinstance(x, str) for x in v)
            for v in parsed0.values()
        ):
            return parsed0
    except json.JSONDecodeError:
        pass

    # strip fences
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) >= 3:
            raw = parts[1].strip()

    # extract JSON array
    start = raw.find('[')
    end = raw.rfind(']') + 1
    if start < 0 or end < 0:
        logger.error("JSON array not found in output: %s", raw)
        raise ValueError("Invalid LLM JSON output")

    try:
        prompt_list = json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s\n%s", e, raw)
        raise

    # validate structure
    for idx, obj in enumerate(prompt_list):
        if not all(k in obj for k in ("category", "framework", "prompt_lines")):
            raise ValueError(f"Missing key in prompt object #{idx}: {obj}")
        if not isinstance(obj["prompt_lines"], list) or not all(isinstance(l, str) for l in obj["prompt_lines"]):
            raise ValueError(f"'prompt_lines' invalid at index {idx}")

    # ——— Group back into { category: [ multi-line-prompt, … ] } ———
    prompts_by_cat: dict[str, list[str]] = {}
    for obj in prompt_list:
        full_prompt = "\n".join(obj["prompt_lines"])
        prompts_by_cat.setdefault(obj["category"], []).append(full_prompt)

    return prompts_by_cat