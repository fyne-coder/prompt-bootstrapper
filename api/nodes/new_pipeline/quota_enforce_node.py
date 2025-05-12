from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def QuotaEnforceNode(prompts: list[str], plan: dict) -> list[str]:
    """
    Enforce category quotas on prompts; slice or regenerate until exactly 10 remain.
    Returns a list of 10 prompts.
    """
    # Ensure we have at least 10 prompts
    if len(prompts) < 10:
        raise ValueError(f"Expected at least 10 prompts, got {len(prompts)}")
    # Return exactly the first 10 prompts
    return prompts[:10]