# System Story (Pharma + Banking + Orchestrator)

## 0) TL;DR (30 seconds)
I built a 3-service GenAI platform deployed on Azure App Service using Docker images,
plus a supporting RAG service:
- Pharma Rewrite API: rewrites pharma emails safely
- Banking Risk Rewriter API: rewrites banking communications + risk flags + disclaimer
- Agent Orchestrator API: single entry point; routes requests to the correct domain service
- RAG Service API: document-grounded answers from uploaded PDFs

Why this matters: separation of domains, reduced blast radius, independent scaling, and clear ownership.

---

## 1) What I built (3 services + RAG support)
### A) Pharma Rewrite API (Azure App Service)
- Docker image: `mofasshara/pharma-email-assistant:rewrite`
- Primary job: rewrite pharma communication (safe, professional)
- Public endpoints:
  - Health: `https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/`
  - Rewrite: `https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/rewrite` (POST)
  - Docs: `https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/docs`

### B) Banking Risk Rewriter API (Azure App Service)
- Docker image: `mofasshara/pharma-email-assistant:banking-v4`
- Primary job: rewrite client communications + classify risk + flag phrases + append disclaimer
- Public endpoints:
  - Health: `https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health`
  - Rewrite: `https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite` (POST)
  - Reviews: `https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/reviews/{trace_id}` (GET)
  - Docs: `https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/docs`

### C) Agent Orchestrator API (Azure App Service)
- Docker image: `mofasshara/pharma-email-assistant:orchestrator-v1`
- Primary job: entry point for clients; routes to Banking or Pharma based on request metadata
- Public endpoints:
  - Health: `https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/agent/health`
  - Handle: `https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/agent/handle` (POST)
  - Docs: `https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/docs`

### D) RAG Service API (Azure App Service)
- Docker image: `mofasshara/pharma-email-assistant:rag-v1`
- Primary job: answer document-grounded questions from uploaded PDFs
- Public endpoints:
  - Health: `https://rag-mofr-fhhseqb2c0etaeh9.westeurope-01.azurewebsites.net/rag/health`
  - Ask: `https://rag-mofr-fhhseqb2c0etaeh9.westeurope-01.azurewebsites.net/rag/ask` (POST)
  - Docs: `https://rag-mofr-fhhseqb2c0etaeh9.westeurope-01.azurewebsites.net/docs`

---

## 2) Why 3 services (Tech Lead reasoning)
### Separation by domain + risk profile
- Banking and pharma have different regulatory tone, disclaimers, and risk rules.
- Orchestrator is a routing/control plane: it can evolve independently without redeploying domain logic.

### Independent release cadence
- Banking rules/policies may change more frequently than pharma prompts.
- Orchestrator changes are integration-focused.

### Independent scaling
- Banking traffic spikes should not slow pharma.
- Orchestrator can be lightweight; domain services can scale separately.

### Blast-radius containment
- If Banking fails (e.g., image pull, bug), Pharma can still operate.
- Orchestrator can degrade gracefully (return a clean error for Banking only).

---

## 3) End-to-end request flow (the important part)
### 3.1 External client -> Orchestrator -> Domain service -> Response (happy path)
**Goal:** client sends one request, orchestrator routes to the correct service, response returned with trace.

#### Flow A — Banking rewrite via Orchestrator
1) Client calls Orchestrator:
   - `POST /agent/handle`
   - Body includes:
     - `domain = "banking"`
     - `email` (the text)
     - `audience` ("client" / "internal")
2) Orchestrator validates inputs (basic schema validation).
3) Orchestrator generates a `request_id` (used for correlation).
4) Orchestrator calls Banking service:
   - `POST https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite`
   - Passes `email`, `audience`, `language`
   - Passes `X-Request-ID` header
5) Banking service:
   - detects risky phrases
   - assigns `risk_level` (low/medium/high)
   - rewrites using deterministic patterns
   - adds disclaimer if audience is client/external
   - returns JSON response (includes `trace_id`)
6) Orchestrator returns:
   - banking response payload
   - `request_id`
7) Optional follow-up:
   - client calls `GET /banking/reviews/{trace_id}` directly on Banking
8) If RAG is enabled and triggered, Banking/Pharma pull grounded context from
   `https://rag-mofr-fhhseqb2c0etaeh9.westeurope-01.azurewebsites.net/rag/ask`.

#### Flow B — Pharma rewrite via Orchestrator
1) Client calls Orchestrator:
   - `POST /agent/handle`
   - Body includes:
     - `email`
     - `audience`
2) Orchestrator routes to Pharma rewrite service.
3) Orchestrator calls Pharma service:
   - `POST https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/rewrite`
   - Passes `text`, `audience`
   - Passes `X-Request-ID` header
4) Pharma service:
   - rewrites the email using prompt rules
   - returns JSON response
5) Orchestrator returns:
   - pharma response payload
   - `request_id`

---

### 3.2 Direct-to-service usage (bypassing Orchestrator)
Some clients (internal testing / demos) may call Banking or Pharma directly:
- Banking direct: `POST /banking/rewrite`
- Pharma direct: `POST /rewrite`

Orchestrator is still valuable because it centralizes routing + standardizes inputs.

---

### 3.3 Correlation / trace_id strategy (what I implemented)
**Objective:** correlate logs and make debugging easy.

- Orchestrator creates a `request_id` for every request.
- Banking service creates a `trace_id` and returns it in the response.
- Orchestrator forwards `X-Request-ID` to downstream services.
- `trace_id` is used for `/banking/reviews/{trace_id}` retrieval.

---

### 3.4 Failure modes + expected behavior (Tech Lead section)
**Banking service down**
- Orchestrator returns a clean error (typically 500/502).
- Pharma still works.

**Timeout calling domain service**
- Orchestrator uses explicit timeouts.
- Returns a clean error with `request_id`.

**Bad input**
- Orchestrator rejects with 422 + validation details.

---

## 4) Key endpoints (prod)
### Orchestrator
- `GET /agent/health`
- `POST /agent/handle`

### Banking
- `GET /banking/health`
- `POST /banking/rewrite`
- `GET /banking/reviews/{trace_id}`

### Pharma
- `GET /`
- `POST /rewrite`
- `GET /docs` and `/openapi.json`

### RAG
- `GET /rag/health`
- `POST /rag/ask`

---

## 5) Reliability + security
### Reliability
- Health checks configured in Azure per app:
  - Orchestrator: `/agent/health`
  - Banking: `/banking/health`
  - Pharma: `/`
- Timeouts: Orchestrator outbound calls have explicit timeout.
- Retries: optional; use only for safe retry logic.

### Security / secrets
- Secrets stored in Azure App Service -> Configuration -> Environment variables
- No secrets in code or repo

### Logging
- Each request logs:
  - request_id
  - domain
  - endpoint
  - status_code
  - latency_ms
- Avoid logging raw email content in production (PII risk).

## 4.1 RAG validation (Week 19)
- RAG health returns 200 OK.
- Pharma responses include `rag_used: true` when triggered.
- Banking rationale includes “RAG context used.” when triggered.

---

## 6) If this were a bank pilot next
- Add AuthN/AuthZ (Entra ID / OAuth) + role-based access
- Add persistent audit trail (Storage/DB) keyed by trace_id
- Add prompt eval gating in CI (block deployments if safety regression)
- Add PII detection/redaction + EU data residency posture
