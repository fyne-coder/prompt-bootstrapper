from api.nodes.fetch_summary_node import Node, _extract_text

@Node(retries=1)
def CleanNode(html: str) -> str:
    """
    Strip HTML boilerplate and extract visible text content.
    Returns cleaned text corpus for analysis.
    """
    # Use existing extractor from FetchSummaryNode
    text = _extract_text(html)
    return text