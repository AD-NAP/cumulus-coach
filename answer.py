import anthropic
from retrieve import retrieve

client = anthropic.Anthropic()
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
               "Tell me more about AWS Glacier and a good chicken rice recipe"]

    for qn in questions:
        print(answer(qn))
