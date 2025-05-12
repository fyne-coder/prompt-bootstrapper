from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def KeyphraseNode(text: str) -> list[str]:
    """
    Extract at least 15 key phrases from the cleaned text for relevance scoring.
    Returns a list of key phrase strings.
    """
    import re
    from collections import Counter

    # Simple keyphrase extraction: top frequent words excluding stopwords
    # Define basic English stopwords
    stopwords = {
        'the', 'and', 'a', 'an', 'of', 'to', 'in', 'for', 'on', 'with', 'as',
        'by', 'at', 'is', 'are', 'was', 'were', 'be', 'been', 'it', 'this',
        'that', 'from', 'or', 'but', 'not', 'your', 'our', 'their', 'its'
    }
    # Normalize text to lowercase and extract words
    words = re.findall(r"\b\w+\b", text.lower())
    # Filter tokens
    tokens = [w for w in words if w not in stopwords and len(w) > 2]
    # Count frequencies
    freq = Counter(tokens)
    # Return top 15 keyphrases (or fewer if not enough)
    keyphrases = [word for word, _ in freq.most_common(15)]
    return keyphrases