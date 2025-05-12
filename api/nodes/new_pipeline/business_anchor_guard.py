from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def BusinessAnchorGuard(prompts: list[str], keyphrases: list[str]) -> list[str]:
    """
    Keep prompts that mention at least one scraped key-phrase.
    If no key-phrases were extracted, return an empty list.
    """
    if not keyphrases:
        return []

    lowered_phrases = [kp.lower() for kp in keyphrases]
    anchored = [
        p for p in prompts
        if any(phrase in p.lower() for phrase in lowered_phrases)
    ]
    return anchored
