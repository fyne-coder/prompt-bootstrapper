import pytest
import openai

from api.nodes.new_pipeline.mini_master_prompt_node import MiniMasterPromptNode

def test_capsule_success(monkeypatch):
    html = "<html><body>Test</body></html>"
    fake_text = "This is a capsule summary."
    class FakeCompletions:
        @staticmethod
        def create(*args, **kwargs):
            class Msg:
                content = fake_text
            class Choice:
                message = Msg()
            class Response:
                choices = [Choice()]
            return Response()

    class FakeClient:
        def __init__(self):
            self.chat = type("Chat", (object,), {"completions": FakeCompletions()})()

    monkeypatch.setattr(openai, "OpenAI", lambda *args, **kwargs: FakeClient())
    capsule = MiniMasterPromptNode(html)
    assert isinstance(capsule, str)
    assert capsule == fake_text

def test_capsule_error(monkeypatch):
    html = "<html>error</html>"
    class FakeCompletions:
        @staticmethod
        def create(*args, **kwargs):
            raise RuntimeError("LLM failure")

    class FakeClient:
        def __init__(self):
            self.chat = type("Chat", (object,), {"completions": FakeCompletions()})()

    monkeypatch.setattr(openai, "OpenAI", lambda *args, **kwargs: FakeClient())
    with pytest.raises(RuntimeError):
        MiniMasterPromptNode(html)