# Interview Q&A

## Why 3 services instead of 1?
- Banking and Pharma are regulated domains with different risk profiles and output requirements
- Orchestrator stays thin (routing + safety boundary), while domain logic lives in Banking and Pharma
- Independent release cadence: banking rule updates don’t force pharma redeploys, and orchestrator stays stable
- Blast-radius containment: banking outage doesn’t break pharma, orchestrator still serves pharma
- Easier compliance reviews: Banking has audit/review endpoints; Pharma stays focused on safe rewriting

## What’s the failure mode if banking goes down?
- Orchestrator returns controlled 502 for downstream banking failures
- Pharma rewrite remains fully available via its own App Service
- Direct access to Banking and Pharma still works without orchestrator
- Timeouts are explicit on orchestrator-to-domain calls to avoid cascading failures

## How do you prevent unsafe outputs?
- Banking uses a deterministic rule layer (risk phrases + disclaimers)
- Pharma uses audience-specific prompts and safety checks
- Orchestrator routes only; it does not alter domain content
- Output schemas are validated (Pydantic) in each domain service

## How do you evaluate prompt quality?
- Evaluation is documented as a roadmap item; current system logs data for future evaluation
- Banking: risk flags + disclaimer presence checks (deterministic)
- Pharma: tone + compliance wording checks planned
- Orchestrator: planned routing/evaluation metrics (coverage by domain)

## How do you handle PII / data residency?
- Pharma logs include input/output (see README logging section)
- Banking audit stores request/response JSONL, including raw content
- Orchestrator can be the centralized place to add redaction middleware
- Deployed on EU-hosted Azure App Services

## How would you add auth for internal bank users?
- Azure AD / Entra ID at Orchestrator layer
- Role-based routing (internal vs external audiences)
- Downstream Banking and Pharma services remain auth-agnostic for separation of concerns

## What would you monitor in production?
- Health endpoints per service (Banking, Pharma, Orchestrator)
- Latency per downstream dependency from Orchestrator
- Error rate by domain (banking vs pharma)
- Volume routed through Orchestrator by domain

## What tradeoffs did you accept to ship faster?
- Separate App Services instead of Kubernetes (all three apps)
- Simple HTTP orchestration instead of async queues (orchestrator to Banking/Pharma)
- Minimal persistence in v1 (Banking JSONL audit only)
- Focus on correctness and explainability over UI
