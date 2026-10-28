from abc import ABC, abstractmethod

from answer import Answer, answer


class Agent(ABC):
    """Every backend answers a question the same way: run(question) -> Answer."""

    @abstractmethod
    def run(self, question: str) -> Answer:
        """Answer one question, using retrieval and tools as the backend sees fit."""


class RagAgent(Agent):
    """Retrieve, then one Claude call, no tools. The baseline the tool-using agent is compared against."""

    def run(self, question: str) -> Answer:
        return answer(question)
