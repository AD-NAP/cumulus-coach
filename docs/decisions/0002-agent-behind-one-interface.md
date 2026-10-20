# 0002. The agent sits behind one interface

Date: 20-10-2026

## Context

The first agent is a plain Claude SDK tool-use loop. A LangGraph version may follow. Both should be compared on the
same eval set.

## Decision

Every agent implements `Agent.run(question) -> Answer`. Retrieval and tools are plain functions that any agent can
call. The CLI and the eval script pick the backend with an option, for example `--agent sdk` or `--agent langgraph`.

## Why

- Adding a backend changes nothing else.
- The eval compares backends fairly: same questions, same retrieval, same tools.

## Trade-offs

- A little more structure up front than a single script.
