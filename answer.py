import anthropic
from retrieve import retrieve

client = anthropic.Anthropic()
MAX_DISTANCE = 1.1  # best chunk further than this: refuse without calling the API
SYSTEM = """You are an AWS study coach.
Follow these 3 rules: 
Grounding: answer only from the excerpts, not general knowledge.
Refusal: if the excerpts don't contain the answer, only reply "I don't know based on the provided AWS documents."
Citations: put the excerpt number, such as [2], after each claim so users can trust your answers."""

def build_prompt(question, notes):
    parts = []
    for i, note in enumerate(notes, start=1):
        parts.append(f"[{i}] (source: {note['source']})\n{note['text']}")
    context = "\n\n".join(parts)
    return f"""{context}

Question: {question}"""

def answer(question):
    notes = retrieve(question, k=3)
    best = notes[0]["distance"]
    if best > MAX_DISTANCE:                     # guard clause: even the best chunk is too far
        print(f"[cutoff] best distance {best:.3f} > {MAX_DISTANCE}, Claude not called")
        return "I don't know based on the provided AWS documents."
    print(f"[claude] best distance {best:.3f}, sent to Claude")

    rag_prompt = build_prompt(question, notes)

    response = client.messages.create(
                model="claude-haiku-5-5",
                system=SYSTEM,
                max_tokens=1024,
                messages=[{"role": "user", "content": rag_prompt}],
            )
    # print(response.usage.input_tokens, "in,", response.usage.output_tokens, "out")
    for block in response.content:
        if block.type == "text":
            return block.text

if __name__ == "__main__":
    questions = ["What is the shared responsibility model?",
               "What are the six advantages of cloud computing?",
               "What is a good pasta recipe?",
               "Tell me more about AWS Glacier and a good chicken rice recipe",
               "Is AWS better than Google Cloud?"]

    for qn in questions:
        print(answer(qn))
        print("\n====================\n")
