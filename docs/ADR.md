# Architecture decision records

One section per decision, oldest first. Each one records the context, the decision, why, and the trade-offs. A new
decision gets the next number at the bottom. A changed decision gets a new record that says which one it replaces.

## 0001. Chroma with local embeddings

Date: 20-10-2026

### Context

The demo needs a vector store and an embedding model. The Claude API doesn't create embeddings, so they come from
somewhere else. The demo must be cheap, run on a laptop and in CI, and be easy for someone else to clone and run.

### Decision

Use Chroma as a local, file-based vector store, with its default embedding model (a small sentence-transformer
that runs on the CPU).

### Why

- No extra API key or cost for embeddings. Only the Claude API needs a key.
- Runs the same on a laptop, in Docker and in CI.
- Chroma lets you swap the embedding function later, for example to a hosted model, and compare it on the eval set.

### Trade-offs

- A small local model retrieves less well than a large hosted one. The eval set will show whether that matters.
- Chroma is not a production database. Fine for a demo; a real service would use a managed store.

## 0002. The agent sits behind one interface

Date: 20-10-2026

### Context

The first agent is a plain Claude SDK tool-use loop. A LangGraph version may follow. Both should be compared on the
same eval set.

### Decision

Every agent implements `Agent.run(question) -> Answer`. Retrieval and tools are plain functions that any agent can
call. The CLI and the eval script pick the backend with an option, for example `--agent sdk` or `--agent langgraph`.

### Why

- Adding a backend changes nothing else.
- The eval compares backends fairly: same questions, same retrieval, same tools.

### Trade-offs

- A little more structure up front than a single script.
