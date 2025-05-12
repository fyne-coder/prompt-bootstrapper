import openai
import pytest

from api.nodes.new_pipeline.web_fetch_node import WebFetchNode

class DummyWSData:
    def __init__(self, data=None, web_pages=None):
        self.data = data
        self.web_pages = web_pages

def test_web_fetch_node_data(monkeypatch):
    # Simulate WebSearch returning data with 'text'
    dummy = DummyWSData(data=[{'text': '<html>hello</html>'}, {'snippet': 'world'}])
    # Ensure openai.WebSearch exists with create()
    class FakeWS:
        @staticmethod
        def create(query):
            return dummy
    monkeypatch.setattr(openai, 'WebSearch', FakeWS, raising=False)
    result = WebFetchNode('http://example.com')
    assert '<html>hello</html>' in result
    assert 'world' in result

def test_web_fetch_node_web_pages(monkeypatch):
    # Simulate WebSearch returning web_pages with 'snippet'
    dummy = DummyWSData(data=None, web_pages=[{'snippet': '<p>foo</p>'}])
    class FakeWS:
        @staticmethod
        def create(query):
            return dummy
    monkeypatch.setattr(openai, 'WebSearch', FakeWS, raising=False)
    result = WebFetchNode('http://example.com')
    assert '<p>foo</p>' in result

def test_web_fetch_node_error(monkeypatch):
    # Simulate WebSearch.create raising an exception
    # Simulate missing or broken WebSearch tool
    class FakeWS:
        @staticmethod
        def create(query):
            raise RuntimeError('fail')
    monkeypatch.setattr(openai, 'WebSearch', FakeWS, raising=False)
    result = WebFetchNode('http://example.com')
    # Should return empty string to trigger fallback
    assert result == ''