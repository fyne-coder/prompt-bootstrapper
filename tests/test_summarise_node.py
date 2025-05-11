import pytest

import api.nodes.summarise_node as sn
import types

class DummyChoice:
    def __init__(self, content):
        class Msg:
            def __init__(self, text):
                self.content = text
        self.message = Msg(content)

class DummyResponse:
    def __init__(self, content):
        self.choices = [DummyChoice(content)]

def test_success(monkeypatch):
    sample = "This is a test business with values, vision, and mission."
    # stub OpenAI client interface
    dummy = DummyResponse("Test prompt for business.")
    class DummyClient:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: dummy
                )
            )
    monkeypatch.setattr(sn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient())
    result = sn.SummariseNode(sample)
    assert result == "Test prompt for business."
    assert len(result) <= 240

def test_truncate(monkeypatch):
    long_content = "x" * 300
    # stub OpenAI client for truncate
    dummy = DummyResponse(long_content)
    class DummyClient2:
        def __init__(self):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda model, messages, temperature: dummy
                )
            )
    monkeypatch.setattr(sn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient2())
    result = sn.SummariseNode("irrelevant")
    assert len(result) == 240

def test_retry(monkeypatch):
    calls = {'n': 0}
    # stub client to simulate failures
    class DummyClient3:
        def __init__(self):
            def create(model, messages, temperature):
                calls['n'] += 1
                raise RuntimeError("API failed")
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=create
                )
            )
    monkeypatch.setattr(sn.openai, 'OpenAI', lambda *args, **kwargs: DummyClient3())
    with pytest.raises(RuntimeError):
        sn.SummariseNode("text")
    # Should retry 3 times
    assert calls['n'] == 3