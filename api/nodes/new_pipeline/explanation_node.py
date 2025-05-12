from api.nodes.fetch_summary_node import Node

@Node(retries=2)
def ExplanationNode(prompts: list[str]) -> list[str]:
    """
    Generate ≤40-word "When to use" tips for each prompt via LLM.
    Returns a list of tip strings matching prompts order.
    """
    raise NotImplementedError("ExplanationNode is not implemented")