import pytest

from api.nodes.new_pipeline.framework_select_node import FrameworkSelectNode

def test_framework_select_node_structure():
    keyphrases = ['term1', 'term2', 'term3'] * 5
    plan = FrameworkSelectNode(keyphrases)
    # Check keys and total count
    expected = {'Marketing': 3, 'Sales': 2, 'Product': 2, 'Success': 1, 'Ops': 1}
    assert isinstance(plan, dict)
    assert set(plan.keys()) == set(expected.keys())
    assert sum(plan.values()) == sum(expected.values())
    assert plan == expected

@pytest.mark.parametrize('empty', ['', None])
def test_framework_select_node_empty(empty):
    # Even if keyphrases empty or None, quota remains constant
    plan = FrameworkSelectNode(empty)
    assert sum(plan.values()) == sum({'Marketing': 3, 'Sales': 2, 'Product': 2, 'Success': 1, 'Ops': 1}.values())