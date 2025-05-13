"""
Node that uses an LLM to fetch and profile a webpage in one shot.
Returns structured JSON with business metadata.
"""
import json
import logging
import openai

from api.nodes.fetch_summary_node import Node
from api.config import OPENAI_MODEL

logger = logging.getLogger(__name__)

@Node(retries=2)
def PageLLMProfileNode(url: str) -> dict:
    """
    One-shot profile of a business homepage via LLM.
    Returns JSON with keys: name, sector, services, geo,
    value_props, brand_tone, keywords.
    """
    client = openai.OpenAI()
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            tools=[{"type": "web_search"}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=400,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are BizScraper-AI. Use web_search to visit the URL, "
                        "gather up to 14 000 chars, and return ONLY valid JSON with: "
                        "name, sector, services (≤5), geo, value_props (3–5), "
                        "brand_tone ['friendly','formal','premium','fun','neutral','playful'], "
                        "keywords (≤8). If missing, use empty string/list."
                    )
                },
                {"role": "user", "content": url, "tool": "web_search"},
            ],
        )
        raw = resp.choices[0].message.content
    except Exception as e:
        logger.error("LLM profile call failed: %s", e)
        raise
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.error("JSON decode error in PageLLMProfileNode: %s", raw[:500])
        # Clear cache entry on parse failure so subsequent calls retry
        try:
            PageLLMProfileNode.cache_clear()
        except Exception:
            pass
        data = {}
    # fill defaults
    for key in ("name", "sector", "geo", "brand_tone"):
        data.setdefault(key, "")
    for key in ("services", "value_props", "keywords"):
        data.setdefault(key, [])
    return data