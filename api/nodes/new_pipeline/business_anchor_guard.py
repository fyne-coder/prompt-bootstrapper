import logging
import re
import collections

from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def BusinessAnchorGuard(prompts, keyphrases_or_capsule):
    """
    Dual-mode anchoring:
    - Legacy mode: prompts=list[str], keyphrases_or_capsule=list[str] => filter by keyphrases.
    - New mode: prompts_by_cat=dict[str,list[str]], keyphrases_or_capsule=capsule(str) => filter by capsule nouns.
    """
    logger = logging.getLogger(__name__)
    # Legacy mode: list of prompts and list of keyphrases
    if isinstance(prompts, list) and isinstance(keyphrases_or_capsule, list):
        keyphrases = keyphrases_or_capsule
        if not keyphrases:
            return prompts
        lowered = [kp.lower() for kp in keyphrases]
        return [p for p in prompts if any(phrase in p.lower() for phrase in lowered)]
    # New mode: dict of categories and capsule text
    if isinstance(prompts, dict) and isinstance(keyphrases_or_capsule, str):
        capsule = keyphrases_or_capsule
        # Extract words of length ≥4 as candidate nouns
        nouns = re.findall(r"\b[A-Za-z]{4,}\b", capsule.lower())
        top_nouns = [w for w, _ in collections.Counter(nouns).most_common(20)]
        anchored = {}
        for cat, items in prompts.items():
            filtered = []
            for p in items:
                lp = p.lower()
                overlap = sum(1 for noun in top_nouns if noun in lp)
                if overlap >= 3:
                    filtered.append(p)
            # fallback if no prompts matched
            anchored[cat] = filtered or items
        return anchored
    # Fallback: return original
    logger.info("BusinessAnchorGuard: unexpected args, returning original prompts")
    return prompts
