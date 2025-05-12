from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def DeduplicateNode(prompts: list[str]) -> list[str]:
    """
    Remove duplicate prompts based on cosine similarity (>85%).
    Returns a list of unique prompts.
    """
    import re
    from math import sqrt

    # Helper: compute cosine similarity between two token count dicts
    def cosine_sim(c1: dict[str, int], c2: dict[str, int]) -> float:
        # dot product
        dot = sum(c1.get(tok, 0) * c2.get(tok, 0) for tok in c1)
        norm1 = sqrt(sum(v * v for v in c1.values()))
        norm2 = sqrt(sum(v * v for v in c2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    # Tokenize and count function
    def count_tokens(text: str) -> dict[str, int]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        counts: dict[str, int] = {}
        for tok in tokens:
            counts[tok] = counts.get(tok, 0) + 1
        return counts

    seen: list[dict[str, int]] = []
    unique_prompts: list[str] = []
    for prompt in prompts:
        counts = count_tokens(prompt)
        # Compare to previously accepted prompts
        duplicate = False
        for prev in seen:
            if cosine_sim(counts, prev) > 0.85:
                duplicate = True
                break
        if not duplicate:
            unique_prompts.append(prompt)
            seen.append(counts)
    return unique_prompts