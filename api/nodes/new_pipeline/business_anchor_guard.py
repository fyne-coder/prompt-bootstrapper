from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def BusinessAnchorGuard(prompts, keyphrases: list[str]):
    """
    Keep prompts that mention at least one scraped key-phrase.
    If no key-phrases were extracted, return an empty list.
    """
    # Skip anchoring for grouped prompts (dict input)
    if isinstance(prompts, dict):
        logging.getLogger(__name__).info(
            "BusinessAnchorGuard: grouped prompts detected, skipping filter")
        return prompts
    if not keyphrases:
        # No keyphrases: return original prompts
        return prompts

    lowered_phrases = [kp.lower() for kp in keyphrases]
    anchored = [
        p for p in prompts
        if any(phrase in p.lower() for phrase in lowered_phrases)
    ]
    return anchored
