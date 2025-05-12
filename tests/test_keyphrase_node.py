import pytest

from api.nodes.new_pipeline.keyphrase_node import KeyphraseNode

def test_keyphrase_node_basic():
    text = (
        "Apple and banana are fruits. "
        "Apple is sweet; banana is yellow. "
        "Orange is citrus fruit; apple and orange both common."
    )
    phrases = KeyphraseNode(text)
    # Expect 'apple', 'banana', 'orange', 'fruits', 'citrus', 'sweet', 'yellow', 'common'
    assert 'apple' in phrases
    assert 'banana' in phrases
    assert 'orange' in phrases
    # Should not include stopwords
    assert 'and' not in phrases
    # Return type and length
    assert isinstance(phrases, list)
    assert all(isinstance(p, str) for p in phrases)

def test_keyphrase_node_empty():
    # Empty text yields empty list
    result = KeyphraseNode("")
    assert result == []