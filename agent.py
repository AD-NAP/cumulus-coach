from abc import ABC, abstractmethod

from answer import (MODEL, REFUSAL, SYSTEM, Answer, answer, build_prompt, client,
                    extract_citations, format_notes)
from retrieve import retrieve
from tools import TOOL_DEFINITIONS, TOOLS

MAX_TURNS = 5  # most Claude calls per question, so a confused model can't loop forever


class Agent(ABC):
    """Every backend answers a question the same way: run(question) -> Answer."""

    @abstractmethod
    def run(self, question: str) -> Answer:
        """Answer one question, using retrieval and tools as the backend sees fit."""


class RagAgent(Agent):
    """Retrieve, then one Claude call, no tools. The baseline the tool-using agent is compared against."""

    def run(self, question: str) -> Answer:
        return answer(question)


class ToolAgent(Agent):
    """Retrieve, then let Claude call tools until it has an answer."""

    def run(self, question: str) -> Answer:
        notes = retrieve(question, k=3)  # excerpts [1] to [3]; tool results continue the numbering
        messages = [{"role": "user", "content": build_prompt(question, notes)}]

        for _ in range(MAX_TURNS):
            response = client.messages.create(
                model=MODEL,
                system=SYSTEM,
                max_tokens=1024,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )
            if response.stop_reason != "tool_use":
                break  # Claude is done asking for tools

            # Claude's reply, tool request included, goes into the history first.
            messages.append({"role": "assistant", "content": response.content})

            results = []
            for block in response.content:
                if block.type == "tool_use":
                    found = TOOLS[block.name](**block.input)  # run the tool Claude asked for
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,  # which request this result answers
                        "content": format_notes(found, start=len(notes) + 1) or "No excerpts found.",
                    })
                    notes.extend(found)
            messages.append({"role": "user", "content": results})

        if response.stop_reason == "tool_use":  # still asking for tools after MAX_TURNS
            return Answer(text=REFUSAL, refused=True)

        text = "".join(block.text for block in response.content if block.type == "text")
        citations = extract_citations(text, notes)
        refused = REFUSAL in text and not citations
        return Answer(text=text, refused=refused, citations=citations)
