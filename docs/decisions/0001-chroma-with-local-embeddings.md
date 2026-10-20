# 0001. Chroma with local embeddings

Date: 20-10-2026

## Context

The demo needs a vector store and an embedding model. The Claude API doesn't create embeddings, so they come from
somewhere else. The demo must be cheap, run on a laptop and in CI, and be easy for someone else to clone and run.

## Decision

Use Chroma as a local, file-based vector store, with its default embedding model (a small sentence-transformer
that runs on the CPU).

## Why

- No extra API key or cost for embeddings. Only the Claude API needs a key.
- Runs the same on a laptop, in Docker and in CI.
- Chroma lets you swap the embedding function later, for example to a hosted model, and compare it on the eval set.

## Trade-offs

- A small local model retrieves less well than a large hosted one. The eval set will show whether that matters.
- Chroma is not a production database. Fine for a demo; a real service would use a managed store.
