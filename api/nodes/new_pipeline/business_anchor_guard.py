from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def BusinessAnchorGuard(prompts: list[str], keyphrases: list[str]) -> list[str]:
    """
    Filter out prompts that do not contain any scraped business keyphrase.
    Returns a list of anchored prompts.
    """
    # Filter prompts that contain at least one key business phrase
    if not keyphrases:
        return []
    anchored: list[str] = []
    lowered_phrases = [kp.lower() for kp in keyphrases]
    for prompt in prompts:
        prompt_lower = prompt.lower()
        for phrase in lowered_phrases:
            if phrase and phrase in prompt_lower:
                anchored.append(prompt)
                break
    return anchored