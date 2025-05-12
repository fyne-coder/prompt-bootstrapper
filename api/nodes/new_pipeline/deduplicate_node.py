from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def DeduplicateNode(prompts: list[str]) -> list[str]:
    """
    Remove duplicate prompts based on cosine similarity (>85%).
    Returns a list of unique prompts.
    """
    raise NotImplementedError("DeduplicateNode is not implemented")