import pytest

from api.nodes.new_pipeline.business_anchor_guard import BusinessAnchorGuard

def test_business_anchor_basic():
    prompts = [
        "Optimize the sales funnel for better revenue",
        "Write a generic introduction to AI",
        "Improve customer success metrics",
    ]
    keyphrases = ["sales", "success"]
    result = BusinessAnchorGuard(prompts, keyphrases)
    # Only prompts containing 'sales' or 'success' remain
    assert result == [
        "Optimize the sales funnel for better revenue",
        "Improve customer success metrics",
    ]

def test_business_anchor_case_insensitive():
    prompts = ["Increase CUSTOMER Loyalty", "Boost Profit Margins"]
    keyphrases = ["customer", "profit"]
    result = BusinessAnchorGuard(prompts, keyphrases)
    assert result == prompts

def test_business_anchor_no_phrases():
    prompts = ["Some prompt"]
    result = BusinessAnchorGuard(prompts, [])
    # No keyphrases: prompts should pass through unchanged
    assert result == prompts

def test_business_anchor_empty_prompts():
    result = BusinessAnchorGuard([], ["term"])
    assert result == []

def test_business_anchor_partial_matches():
    prompts = ["Analyze business data", "Understandingness is key"]
    keyphrases = ["business"]
    result = BusinessAnchorGuard(prompts, keyphrases)
    # Only the prompt with exact 'business' word match should remain
    assert result == ["Analyze business data"]