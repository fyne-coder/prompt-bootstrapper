import pytest

from api.nodes.new_pipeline.clean_node import CleanNode

@pytest.mark.parametrize("html, expected", [
    ("<h1>Title</h1><p>Paragraph</p>", "Title Paragraph"),
    ("<div>Line1<br>Line2</div>", "Line1 Line2"),
    ("<html><body><h2>Sub</h2><ul><li>Item1</li><li>Item2</li></ul></body></html>",
     "Sub Item1 Item2"),
])
def test_clean_node_basic(html, expected):
    result = CleanNode(html)
    # Collapse whitespace for comparison
    normalized = " ".join(result.split())
    assert normalized == expected

def test_clean_node_empty():
    # Empty HTML returns empty string
    assert CleanNode("") == ""