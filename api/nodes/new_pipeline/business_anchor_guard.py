from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def BusinessAnchorGuard(prompts, keyphrases: list[str]):
    """
    Keep prompts that mention at least one scraped key-phrase.
    If no key-phrases were extracted, return an empty list.
    """
    if not keyphrases:
        # No keyphrases: do not filter; return original prompts
        return prompts
    # If grouped dict, apply per category
    if isinstance(prompts, dict):
        return {cat: BusinessAnchorGuard(items, keyphrases) for cat, items in prompts.items()}

    lowered_phrases = [kp.lower() for kp in keyphrases]
    anchored = [
        p for p in prompts
        if any(phrase in p.lower() for phrase in lowered_phrases)
    ]
    return anchored
