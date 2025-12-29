# Week 19 Rehearsal Script (10 minutes max)

## 0) Opening (20–30 seconds)
Hi, I’m going to walk you through a production-ready, three-service GenAI platform I built and deployed on Azure. The goal is simple: show domain separation, auditability, and operational discipline in regulated environments. I’ll keep it concise and practical.

## 1) The 30-second overview (40–60 seconds)
I run three independent App Services:
1) **Pharma Email Rewriter** — rewrites pharma communications safely.
2) **Banking Risk Rewriter** — rewrites banking emails, flags risk phrases, adds disclaimers, and supports review workflows.
3) **Agent Orchestrator** — a thin control plane that routes requests to the right domain service.

Why this matters: I can deploy, scale, and audit each domain independently without breaking the others.

## 2) Architecture and why it’s credible (60–90 seconds)
The orchestrator is intentionally thin. It doesn’t do domain logic — it routes and enforces basic safety.  
Banking and pharma are separated because they have different regulatory requirements, different prompts, and different review workflows.  
This gives me independent release cadence and a smaller blast radius: if banking is down, pharma still works.

## 3) Banking flow (2 minutes)
In banking, I receive a client email and return:
- a rewritten email,
- risk level (low/medium/high),
- flagged phrases,
- a disclaimer if needed,
- and a trace_id for audit review.

That trace_id is the audit handle. A reviewer can fetch the exact rewrite later via `/banking/reviews/{trace_id}`.  
This is the part hiring managers care about: deterministic rules, auditability, and an explicit review loop.

## 4) Pharma flow (1–1.5 minutes)
Pharma is simpler but still regulated. The service takes:
- the draft text,
- the target audience,
and returns a safer, more compliant rewrite.

It’s deployed independently, so it can evolve without touching banking.  
The output is designed for compliance language and tone, and it’s easy to evaluate through logged inputs and outputs.

## 5) Orchestrator flow (1–1.5 minutes)
The orchestrator is the entry point for clients who don’t want to think about service boundaries.  
It accepts a request, routes by domain, and forwards it to the right service.  
It also attaches a request_id for tracing so I can correlate logs across services.

It can route to banking or pharma today, and it has a clear extension point for more domains later.

## 6) Ops readiness (60–90 seconds)
I configured health endpoints for all three services, and I validate logs in Azure’s Log Stream for signal, not debugging.  
Key configuration is stored in App Service settings — no secrets in code.  
Each service can be monitored independently for latency and errors.

This is the kind of setup you want before you scale.

## 7) Tradeoffs and next steps (45–60 seconds)
To ship fast, I chose App Services instead of Kubernetes and used simple HTTP orchestration instead of queues.  
Next steps are straightforward:
- add authentication,
- add deeper evaluation in CI,
- and add redaction middleware for PII.

## 8) Close (20–30 seconds)
If you want, I can demo any of the flows live — banking rewrite plus audit lookup, pharma rewrite, or orchestrator routing.  
The key takeaway is: this isn’t just an LLM demo, it’s a production‑oriented, regulated‑ready platform.
