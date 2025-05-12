from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def FrameworkSelectNode(keyphrases: list[str]) -> dict:
    """
    Determine the frameworks mix (RTF, RISEN, CRISPE) per PRD category quotas.
    Returns a plan dict, e.g., {'Marketing':3,'Sales':2,...}.
    """
    # Fixed category quota: 3 Marketing, 2 Sales, 2 Success, 2 Product, 1 Ops
    return {
        'Marketing': 3,
        'Sales': 2,
        'Success': 2,
        'Product': 2,
        'Ops': 1,
    }