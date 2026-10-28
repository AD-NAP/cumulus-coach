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
