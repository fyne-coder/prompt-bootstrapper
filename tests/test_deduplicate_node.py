import pytest

from api.nodes.new_pipeline.deduplicate_node import DeduplicateNode

def test_deduplicate_no_duplicates():
    prompts = ["Fast action items", "Improve sales process", "Review profit margins"]
    result = DeduplicateNode(prompts)
    assert result == prompts

def test_deduplicate_exact_duplicates():
    prompts = ["Do X now", "Do X now", "Do Y later"]
    result = DeduplicateNode(prompts)
    assert result == ["Do X now", "Do Y later"]

def test_deduplicate_similar_prompts():
    # Prompts with high token overlap
    p1 = "Optimize the sales funnel"  # baseline
    p2 = "Optimize sales funnel process"  # very similar
    p3 = "Generate marketing strategy"  # distinct
    result = DeduplicateNode([p1, p2, p3])
    # With 85% similarity threshold, these prompts are not considered duplicates
    assert result == [p1, p2, p3]

def test_deduplicate_empty():
    assert DeduplicateNode([]) == []

def test_deduplicate_partial_overlap():
    # Low overlap should not be filtered
    p1 = "Increase user engagement"
    p2 = "Analyze user data for insights"
    result = DeduplicateNode([p1, p2])
    assert result == [p1, p2]