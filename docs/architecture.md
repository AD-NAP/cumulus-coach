# Architecture

## Overview

```
          ingest (offline)                          ask (online)
  AWS docs -> load -> chunk -> embed -> Chroma
                                          ^
                                          | retrieve(query)
  question -> Agent.run() ----------------+----> tools (quiz, service lookup)
                 |
                 v
              Answer (text, citations, tool calls)
```

## Components

- **Ingest.** Downloads a fixed list of public AWS docs, splits them into chunks, embeds each chunk and stores it in
  a local Chroma collection with its source and section.
- **Retrieval.** `retrieve(query, k)` returns the top chunks with their sources. A plain function, so any agent can
  call it.
- **Tools.** Plain functions with typed inputs: `quiz(topic)` and `lookup_service(name)`. They don't know which
  agent calls them.
- **Agent.** One interface, `Agent.run(question) -> Answer`. The first backend is a plain Claude SDK tool-use loop.
  A LangGraph backend can plug in later with no changes elsewhere.
- **Eval.** A script runs a fixed question set against a chosen backend and reports accuracy, tool-call success,
  latency and tokens.

## Not decided yet

- Chunk size and overlap. Start simple and measure with the eval set.
- Which Claude model. Pick on cost and eval results.
