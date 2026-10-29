import pytest

import agent
from agent import Agent, RagAgent
from answer import Answer


def test_agent_cannot_be_created_directly():
    with pytest.raises(TypeError):
        Agent()


def test_backend_without_run_cannot_be_created():
    class Forgetful(Agent):
        pass

    with pytest.raises(TypeError):
        Forgetful()


def test_rag_agent_is_an_agent():
    assert isinstance(RagAgent(), Agent)


def test_rag_agent_returns_what_answer_returns(monkeypatch):
    fake = Answer(text="fake", refused=False, citations=["url-A"])
    monkeypatch.setattr(agent, "answer", lambda question: fake)  # no Chroma, no API call
    assert RagAgent().run("anything") is fake


# --- ToolAgent: a fake client plays Claude's part, so no API call and no Chroma ---

from types import SimpleNamespace

from agent import MAX_TURNS, ToolAgent


class FakeClient:
    """Stands in for anthropic.Anthropic(): returns scripted replies and records what it was sent."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.messages = self  # so client.messages.create(...) reaches create below

    def create(self, **kwargs):
        self.calls.append(list(kwargs["messages"]))  # a copy, because the agent keeps appending
        return self.replies.pop(0)


def reply(stop_reason, *blocks):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks))


ASK_FOR_SQS = SimpleNamespace(type="tool_use", id="t1", name="lookup_service",
                              input={"name": "Amazon Simple Queue Service"})
THREE_NOTES = [{"text": f"chunk {i}", "source": f"url-{i}"} for i in (1, 2, 3)]


def test_tool_agent_runs_the_tool_and_cites_its_result(monkeypatch):
    fake = FakeClient([
        reply("tool_use", ASK_FOR_SQS),
        reply("end_turn", SimpleNamespace(type="text", text="SQS queues messages [4].")),
    ])
    monkeypatch.setattr(agent, "client", fake)
    monkeypatch.setattr(agent, "retrieve", lambda question, k: list(THREE_NOTES))
    monkeypatch.setattr(agent, "TOOLS", {
        "lookup_service": lambda name: [{"text": "SQS queues messages.", "source": "url-sqs"}],
    })

    result = ToolAgent().run("what does sqs do?")

    assert len(fake.calls) == 2                      # asked for a tool, then answered
    tool_result = fake.calls[1][-1]["content"][0]    # last message of the second call
    assert tool_result["tool_use_id"] == "t1"        # matched to Claude's request
    assert tool_result["content"].startswith("[4]")  # numbering continues after the 3 notes
    assert result.citations == ["url-sqs"]
    assert result.refused is False


def test_tool_agent_gives_up_after_max_turns(monkeypatch):
    fake = FakeClient([reply("tool_use", ASK_FOR_SQS)] * MAX_TURNS)  # never stops asking
    monkeypatch.setattr(agent, "client", fake)
    monkeypatch.setattr(agent, "retrieve", lambda question, k: list(THREE_NOTES))
    monkeypatch.setattr(agent, "TOOLS", {"lookup_service": lambda name: []})

    result = ToolAgent().run("anything")

    assert len(fake.calls) == MAX_TURNS
    assert result.refused is True
