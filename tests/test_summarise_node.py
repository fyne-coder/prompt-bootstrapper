import pytest

import api.nodes.summarise_node as sn

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
    # stub ChatCompletion.create
    def fake_create(model, messages, temperature):
        return DummyResponse("Test prompt for business.")
    monkeypatch.setattr(sn.openai.ChatCompletion, 'create', fake_create)
    result = sn.SummariseNode(sample)
    assert result == "Test prompt for business."
    assert len(result) <= 240

def test_truncate(monkeypatch):
    long_content = "x" * 300
    def fake_create(model, messages, temperature):
        return DummyResponse(long_content)
    monkeypatch.setattr(sn.openai.ChatCompletion, 'create', fake_create)
    result = sn.SummariseNode("irrelevant")
    assert len(result) == 240

def test_retry(monkeypatch):
    calls = {'n': 0}
    def fake_create(model, messages, temperature):
        calls['n'] += 1
        raise RuntimeError("API failed")
    monkeypatch.setattr(sn.openai.ChatCompletion, 'create', fake_create)
    with pytest.raises(RuntimeError):
        sn.SummariseNode("text")
    # Should retry 3 times
    assert calls['n'] == 3