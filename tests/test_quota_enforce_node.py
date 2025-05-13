import pytest

from api.nodes.new_pipeline.quota_enforce_node import QuotaEnforceNode

def test_quota_enforce_exact():
    # Single category with exact prompts matches
    prompts = [f"P{i}" for i in range(10)]
    result = QuotaEnforceNode({'Marketing': prompts}, {'Marketing': 3})
    # Category 'Marketing' should contain up to quota (3)
    assert isinstance(result, dict)
    assert result['Marketing'] == prompts[:3]

def test_quota_enforce_more():
    # More prompts than quota; trim to quota
    prompts = [f"P{i}" for i in range(15)]
    result = QuotaEnforceNode({'Marketing': prompts}, {'Marketing': 3})
    assert len(result['Marketing']) == 3
    assert result['Marketing'] == prompts[:3]

def test_quota_enforce_too_few():
    # No plan entries means no categories; returns empty dict
    prompts = ["P0", "P1", "P2"]
    result = QuotaEnforceNode({'Marketing': prompts}, {})
    assert result == {}