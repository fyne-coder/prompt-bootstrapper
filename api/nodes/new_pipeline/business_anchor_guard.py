from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def BusinessAnchorGuard(prompts: list[str], keyphrases: list[str]) -> list[str]:
    """
    Filter out prompts that do not contain any scraped business keyphrase.
    Returns a list of anchored prompts.
    """
    raise NotImplementedError("BusinessAnchorGuard is not implemented")