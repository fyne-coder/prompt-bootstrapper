import json
import logging

import pytest
import openai

from api.nodes.page_llm_profile_node import PageLLMProfileNode

def test_profile_success(monkeypatch):
    mock_data = {
        "name": "Acme",
        "sector": "Roofing",
        "services": ["repair"],
        "geo": "Boston",
        "value_props": ["fast"],
        "brand_tone": "friendly",
        "keywords": ["roof", "chimney"],
    }
    mock_json = json.dumps(mock_data)
    class FakeCompletions:
        @staticmethod
        def create(*args, **kwargs):
            class Msg:
                content = mock_json
            class Choice:
                message = Msg()
            class Response:
                choices = [Choice()]
            return Response()

    class FakeClient:
        def __init__(self):
            self.chat = type("Chat", (object,), {"completions": FakeCompletions()})()

    monkeypatch.setattr(openai, "OpenAI", lambda *args, **kwargs: FakeClient())
    res = PageLLMProfileNode("http://example.com")
    assert res == mock_data

def test_profile_defaults_on_decode_error(monkeypatch, caplog):
    invalid = "{not valid json}"
    class FakeCompletions:
        @staticmethod
        def create(*args, **kwargs):
            class Msg:
                content = invalid
            class Choice:
                message = Msg()
            class Response:
                choices = [Choice()]
            return Response()

    class FakeClient:
        def __init__(self):
            self.chat = type("Chat", (object,), {"completions": FakeCompletions()})()

    monkeypatch.setattr(openai, "OpenAI", lambda *args, **kwargs: FakeClient())
    caplog.set_level(logging.ERROR)
    res = PageLLMProfileNode("http://example.com")
    # Defaults on JSON error
    assert res["name"] == ""
    assert isinstance(res["services"], list) and res["services"] == []
    assert "JSON decode error" in caplog.text