from api.nodes.fetch_summary_node import Node
from api.nodes.new_pipeline.prompt_draft_node import QUOTAS

@Node(retries=1)
def FrameworkSelectNode(keyphrases: list[str]) -> dict:
    """
    Determine the frameworks mix (RTF, RISEN, CRISPE) per PRD category quotas.
    Returns a plan dict, e.g., {'Marketing':3,'Sales':2,...}.
    """
    # Use unified quotas from PromptDraftNode
    return QUOTAS