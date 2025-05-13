from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def QuotaEnforceNode(prompts_by_cat: dict[str, list[str]], plan: dict) -> dict[str, list[str]]:
    """
    Enforce category quotas on prompts; slice or regenerate until exactly 10 remain.
    Returns a list of 10 prompts.
    """
    """
    Enforce category quotas on grouped prompts; trim each category list to its quota.
    Silently allow fewer if not enough prompts present.
    Returns a dict mapping each category to its trimmed list.
    """
    trimmed: dict[str, list[str]] = {}
    for category, quota in plan.items():
        items = prompts_by_cat.get(category, []) or []
        # Slice to at most quota
        if isinstance(items, list):
            trimmed[category] = items[:quota]
        else:
            trimmed[category] = []
    return trimmed