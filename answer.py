import re
from dataclasses import dataclass, field

import anthropic
from retrieve import retrieve


@dataclass
class Answer:
    text: str
    refused: bool
    citations: list[str] = field(default_factory=list)  # source URLs, a new list per Answer


client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"  # one place to change the model for every agent
MAX_DISTANCE = 1.1  # best chunk further than this: refuse without calling the API
REFUSAL = "I don't know based on the provided AWS documents."
SYSTEM = f"""You are an AWS study coach.
Follow these 3 rules:
Grounding: answer only from the excerpts, not general knowledge.
Refusal: if the excerpts don't contain the answer, only reply "{REFUSAL}"
Citations: put the excerpt number, such as [2], after each claim so users can trust your answers."""

def format_notes(notes, start=1):
    """Number the excerpts [start], [start+1], ... with their sources, so Claude can cite them."""
    parts = []
    for i, note in enumerate(notes, start=start):
        parts.append(f"[{i}] (source: {note['source']})\n{note['text']}")
    return "\n\n".join(parts)

def build_prompt(question, notes):
    return f"""{format_notes(notes)}

Question: {question}"""

def extract_citations(text, notes):
    """Turn [n] markers in the text into the source URLs of the cited notes, in order, without repeats."""
    sources = []
    for number in re.findall(r"\[(\d+)\]", text):    # "[1] ... [3]" -> ["1", "3"]
        i = int(number) - 1                           # [1] is notes[0]
        if 0 <= i < len(notes):                       # ignore numbers Claude made up
            source = notes[i]["source"]
            if source not in sources:                 # two chunks can share one page
                sources.append(source)
    return sources

def answer(question):
    notes = retrieve(question, k=3)
    best = notes[0]["distance"]
    if best > MAX_DISTANCE:                     # guard clause: even the best chunk is too far
        print(f"[cutoff] best distance {best:.3f} > {MAX_DISTANCE}, Claude not called")
        return Answer(text=REFUSAL, refused=True)
    print(f"[claude] best distance {best:.3f}, sent to Claude")

    rag_prompt = build_prompt(question, notes)

    response = client.messages.create(
                model=MODEL,
                system=SYSTEM,
                max_tokens=1024,
                messages=[{"role": "user", "content": rag_prompt}],
            )
    # print(response.usage.input_tokens, "in,", response.usage.output_tokens, "out")
    text = "".join(block.text for block in response.content if block.type == "text")
    citations = extract_citations(text, notes)
    refused = REFUSAL in text and not citations  # a cited partial answer still counts as answered
    return Answer(text=text, refused=refused, citations=citations)

if __name__ == "__main__":
    questions = ["What is the shared responsibility model?",
               "What are the six advantages of cloud computing?",
               "What is a good pasta recipe?",
               "Tell me more about AWS Glacier and a good chicken rice recipe",
               "Is AWS better than Google Cloud?"]

    for qn in questions:
        result = answer(qn)
        print(f"refused={result.refused}")
        print(result.text)
        print("citations:", result.citations)
        print("\n====================\n")
