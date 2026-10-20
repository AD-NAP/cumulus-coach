# cumulus-coach

An agentic AWS study coach. Ask it a question and it answers from public AWS documentation, with
citations. It can also quiz you on a topic and look up an AWS service by name.

Built to learn and show the pieces of an LLM application: retrieval (RAG), tool calling, structured outputs,
evaluation, tests, Docker and CI.

## Status

Work in progress, started 20-10-2026.

## Planned features

- Answers grounded in public AWS docs, with citations. Says "I don't know" when nothing relevant is found.
- Two tools: a quiz on a topic, and a service lookup by name.
- Structured output for every answer.
- An eval set of 20 questions, with accuracy, tool-call success, latency and token use.
- Two agent backends behind one interface: a plain Claude SDK loop, then LangGraph.
- pytest, Docker and GitHub Actions CI.

## Stack

Python, the Claude API, Chroma, pytest, Docker, GitHub Actions.

## Data

Only public AWS documentation. The documents are downloaded by the ingest script and are not committed.

## Docs

- [Architecture](docs/architecture.md)
- [Decisions](docs/decisions/)
