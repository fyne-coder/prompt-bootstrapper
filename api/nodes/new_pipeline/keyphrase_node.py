"""
Legacy keyphrase extraction node retained for backward compatibility.
"""
import logging

from api.nodes.fetch_summary_node import Node

logger = logging.getLogger(__name__)

@Node(retries=1)
def KeyphraseNode(text: str) -> list[str]:
    """
    Extract key-phrases from the given text.
    Legacy stub: returns an empty list; override via pipeline node or tests.
    """
    logger.warning("KeyphraseNode is deprecated; returning empty list.")
    return []