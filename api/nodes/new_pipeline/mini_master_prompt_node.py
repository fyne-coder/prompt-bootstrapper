"""
Node to condense raw HTML into a business context capsule via LLM.
"""
import functools
import logging
import openai

from api.nodes.fetch_summary_node import Node
from api.config import OPENAI_MODEL

logger = logging.getLogger(__name__)

@functools.lru_cache(maxsize=128)
@Node(retries=2)
def MiniMasterPromptNode(html: str) -> str:
    """
    Condense supplied HTML into a ≤350-word Business Context Capsule.
    """
    client = openai.OpenAI()
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "text"},
            temperature=0.3,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Condense the supplied HTML into a ≤350-word Business Context Capsule "
                        "(USPs, services, tone, geo, benefits). Return plain text."
                    ),
                },
                {"role": "user", "content": html[:14000]},
            ],
        )
        capsule = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error("MiniMasterPromptNode LLM error: %s", e)
        raise
    return capsule