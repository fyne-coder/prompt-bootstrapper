import pytest

from api.nodes.new_pipeline.quota_enforce_node import QuotaEnforceNode

def test_quota_enforce_exact():
    prompts = [f"P{i}" for i in range(10)]
    result = QuotaEnforceNode(prompts, {'Marketing':3})
    assert result == prompts

def test_quota_enforce_more():
    prompts = [f"P{i}" for i in range(15)]
    result = QuotaEnforceNode(prompts, {'Marketing':3})
    assert len(result) == 10
    assert result == prompts[:10]

def test_quota_enforce_too_few():
    prompts = ["P0", "P1", "P2"]
    with pytest.raises(ValueError) as exc:
        QuotaEnforceNode(prompts, {})
    assert "Expected at least 10 prompts" in str(exc.value)