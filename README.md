# cumulus-coach

[![CI](https://github.com/AD-NAP/cumulus-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/AD-NAP/cumulus-coach/actions/workflows/ci.yml)

An agentic AWS study coach. Ask it a question and it answers from public AWS documentation, with citations. When
the retrieved excerpts aren't enough, it calls a tool to look up an AWS service by name. When the documents don't
cover a question, it says so instead of guessing.

Built to learn and show the pieces of an LLM application: retrieval (RAG), tool calling, structured outputs,
grounding, tests and CI.

## What works today

- **RAG with citations.** Public AWS doc pages are chunked, embedded locally and stored in Chroma. The top 3 chunks
  go to Claude as numbered excerpts, and every claim in the answer cites one, such as `[2]`.
- **Two refusal layers.** A distance cutoff in code refuses far-off questions without calling the API, so they cost
  nothing. The cutoff (1.1) was picked from measured distances on 18 on-topic, near-topic and off-topic questions.
  The system prompt then refuses anything the excerpts don't support, including the off-topic half of a mixed
  question.
- **Structured output.** Every answer is an `Answer` with `text`, `refused` and `citations` (source URLs, parsed
  from the `[n]` markers).
- **A tool-using agent.** `ToolAgent` runs a Claude tool-use loop: Claude asks for `lookup_service`, the code runs it
  and sends the result back, until Claude has an answer. It's capped at 5 rounds. Tool results continue the excerpt
  numbering, so they can be cited too.
- **One interface for agents.** `Agent.run(question) -> Answer`. `RagAgent` (retrieve, then one call) is the
  baseline, and `ToolAgent` plugs in beside it, so both can be compared on the same questions.
- **Tests and CI.** 18 pytest tests run on every push with GitHub Actions. Claude and Chroma are replaced with fakes,
  so tests are free and need no API key.

## Example

```text
Q: In one line each, what do sqs, lambda and dynamodb do?

Round 1  Claude: tool_use lookup_service(name="Amazon Simple Queue Service")
         code:   runs the lookup, sends back excerpt [4]
Round 2  Claude: end_turn

- Lambda: Runs your code without provisioning or managing servers, and you pay only for the compute time you use [3].
- DynamoDB: A fully managed key-value and document database that delivers single-digit millisecond performance at any scale [1].
- SQS: I don't know based on the provided AWS documents.

refused=False, citations=[compute-services.html, database.html]
```

Claude turned "sqs" into the official name because the tool description asks for it. The lookup found only a
passing mention of SQS, so Claude refused that part instead of answering from general knowledge.

## Run it

Needs Python 3.14 and an [Anthropic API key](https://console.anthropic.com/).

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash; use .venv/bin/activate on macOS or Linux
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...       # or setx on Windows, then open a new terminal
python ingest.py                   # downloads the AWS pages and builds the local Chroma index in ./data
python -c "from agent import ToolAgent; print(ToolAgent().run('What does AWS Lambda do?'))"
python -m pytest                   # no API key needed
```

## How it fits together

| File | Job |
|---|---|
| `ingest.py` | Download 10 public AWS doc pages, chunk them (500 words, 50 overlap), store them in Chroma |
| `retrieve.py` | `retrieve(query, k)`: top chunks by meaning, with source and distance |
| `answer.py` | Prompt, system rules, distance cutoff, one Claude call, `Answer` with citations |
| `tools.py` | `lookup_service(name)`: exact-name search, plus the tool definition Claude sees |
| `agent.py` | The `Agent` interface, `RagAgent` and `ToolAgent` |

More detail in [Architecture](docs/architecture.md) and the [decision records](docs/decisions/).

## Stack

Python, the Claude API (Haiku 5.5 for development), Chroma with local embeddings, pytest, GitHub Actions.

## Next

- An eval set of about 20 questions, comparing `RagAgent` and `ToolAgent` on accuracy, refusals, tool use, latency
  and tokens.
- One measured improvement against the eval (chunking or prompt).
- Better `lookup_service` ranking (a passing mention can outrank the real description), and a `quiz` tool.
- Logging and a Dockerfile.
- A second backend (LangGraph) behind the same `Agent` interface.

## Data

Only public AWS documentation. The pages are downloaded by `ingest.py` and are not committed.
