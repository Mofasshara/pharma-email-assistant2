# Agents

Skeleton layout for agents, tools, and prompts.

- orchestrator.py: central coordinator (router/dispatcher).
- tools/: individual tool wrappers.
- prompts/: reusable prompt templates.
# Week 9 — Agentic Orchestration

## Architecture
User request → Router Agent
→ decides:
  - Use RAG (facts needed)
  - Use Rewrite (style only)
→ Evaluator Agent checks output
→ Final response returned via API

## Why Agents
- Fine-tuning = style
- RAG = facts
- Agents = decision-making
