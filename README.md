# Pharma + Banking GenAI Platform

A multi-service FastAPI platform with three domain-separated apps
(banking, pharma, orchestrator) plus a dedicated RAG service.

## Service Split Summary
- Banking Risk Rewriter: `/banking/*` endpoints and audit/review flow.
- Agent Orchestrator: `/agent/*` endpoints only (no banking/pharma routes).
- Pharma Email Rewriter: `/rewrite` and `/feedback` endpoints.
- RAG Service: `/rag/*` endpoints for document-grounded answers.

## Jump to
- [Banking](#banking-client-communication-risk-rewriter-finma-style-guardrails)
- [Orchestrator](#live-deployments-azure)
- [Pharma](#pharma-email-assistant)

## Live Deployments (Azure)
- Banking Risk Rewriter API: https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/docs
- Agent Orchestrator API: https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/docs
- Pharma Email Rewriter API: https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/docs
- RAG Service API: https://rag-mofr-fhhseqb2c0etaeh9.westeurope-01.azurewebsites.net/docs

## Orchestrator (Agent) Overview
In simple words: the orchestrator is the "traffic controller" that receives a request,
picks the right tool (like the rewrite service), and returns the result with a request ID.

Endpoints:
- `GET /agent/health`
- `POST /agent/handle`
- `GET /agent/deps`

### Quick User Guide (Orchestrator)
1) Open: https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/docs
2) Click **POST /agent/handle** → **Try it out**.
3) Paste a body and click **Execute**.
4) For banking, include `"domain": "banking"`.

Example (pharma):
```json
{
  "email": "Please rewrite this client update for clarity.",
  "audience": "client"
}
```

Example (banking):
```json
{
  "email": "This product will give you excellent returns and is risk-free.",
  "audience": "client",
  "domain": "banking"
}
```

### How to use each endpoint (Orchestrator)
`GET /agent/health`
- Purpose: quick uptime check (should return 200 OK).
- Use it when you want to verify the service is running.

`POST /agent/handle`
- Purpose: the main entry point that routes your request.
- Use it to rewrite a pharma email, or add `"domain":"banking"` to route to banking.
- Example body (pharma):
```json
{
  "email": "Please rewrite this client update for clarity.",
  "audience": "client"
}
```
- Example body (banking):
```json
{
  "email": "This product will give you excellent returns and is risk-free.",
  "audience": "client",
  "domain": "banking"
}
```

`GET /agent/deps`
- Purpose: checks if the downstream rewrite service is reachable.
- Use it for debugging if `/agent/handle` is failing.

Routing rule:
- If `domain` is `"banking"`, it routes to the banking rewrite service.
- Otherwise it routes to the pharma rewrite service (default).
- It may choose RAG if the router decides the request needs retrieval (via `RAG_API_URL`).

Orchestrator smoke test:
```bash
curl -i -X POST https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/agent/handle \
  -H "Content-Type: application/json" \
  -d '{"email":"Test email for orchestrator","audience":"client"}'
```

Example response (real):
```json
{
  "response": {
    "rewritten_email": "Subject: Coordination of Upcoming Medical Affairs Initiatives\n\nDear Team,\n\nI hope this message finds you well. This email serves as a preliminary communication regarding the orchestration of our upcoming initiatives within the Medical Affairs department. \n\nPlease prepare to discuss the objectives and timelines associated with these initiatives in our next meeting. Your insights and expertise will be invaluable in ensuring our efforts align with our strategic goals.\n\nThank you for your attention to this matter.\n\nBest regards,\n\n[Your Name]\n[Your Position]",
    "metadata": {
      "latency_ms": 4813,
      "tokens": {
        "prompt_tokens": 99,
        "completion_tokens": 193,
        "total_tokens": 292
      },
      "model": "gpt-4o-mini"
    }
  },
  "request_id": "1744716d-72e0-4186-a2f4-b5cb72fe671c"
}
```

### How it works (step-by-step)
1) Receive request at `POST /agent/handle`.
2) Generate a `request_id` for traceability.
3) If `domain="banking"`, call the banking rewrite tool.
4) Otherwise, choose between RAG and pharma rewrite.
5) Run safety evaluation on the output.
6) Return the response with `request_id`.

Orchestrator banking route (real):
```bash
curl -i -X POST https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/agent/handle \
  -H "Content-Type: application/json" \
  -d '{"email":"This product will give you excellent returns and is risk-free.","audience":"client","domain":"banking"}'
```

Example response (real):
```json
{
  "response": {
    "rewritten_email": "This product may give you excellent returns and is lower-risk.\n\nDisclaimer: This message is for information purposes only and does not constitute investment advice. Any decision should be based on your risk profile and suitability assessment.\n",
    "risk_level": "medium",
    "flagged_phrases": [
      "risk-free",
      "will give you excellent returns"
    ],
    "disclaimer_added": true,
    "trace_id": "7d2353da-ce21-41a7-b728-49532204fde6",
    "created_at": "2025-12-26T19:46:36.658976Z",
    "review_status": "pending",
    "rationale": "Detected 2 risky phrase(s). Risk classified as medium. Added disclaimer."
  },
  "request_id": "ab484424-dc91-45b1-8455-4fe42994929f"
}
```

## Banking Client Communication Risk Rewriter (FINMA-style guardrails)
A FastAPI service that rewrites relationship-manager emails to reduce regulatory/compliance risk.
It classifies risk level, flags risky phrases, and injects a disclaimer when needed.

### What it does
Given:
- `email`: client message draft
- `audience`: e.g. `client`, `internal`, `external`
- `language`: default `en`

Returns:
- `rewritten_email`
- `risk_level` (`low` | `medium` | `high`)
- `flagged_phrases` (list)
- `disclaimer_added` (bool)
- `rationale` (short explanation)

### Quick User Guide (Banking)
1) Open: https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/docs
2) Click **POST /banking/rewrite** → **Try it out**.
3) Paste a body and click **Execute**.
4) Copy the `trace_id` if you want to fetch the audit record.

Example:
```json
{
  "email": "This product will give you excellent returns and is risk-free. You should buy today.",
  "audience": "client",
  "language": "en"
}
```

### How it works (step-by-step)
1) Receive request at `POST /banking/rewrite`.
2) Normalize input and scan for risky phrases.
3) Classify risk level (low/medium/high).
4) Rewrite risky language with safer phrasing.
5) Append disclaimer for client/external audiences.
6) Generate `trace_id` + `created_at` and store audit record.
7) Return the structured response.

### Banking API
What it does:
- Rewrites client-facing drafts to remove risky language.
- Flags risky phrases and adds a disclaimer when needed.

Why banks care:
- Compliance-safe rewriting and audit-friendly rationale.

Endpoints:
- `GET /banking/health`
- `POST /banking/rewrite`
- `GET /banking/reviews`
- `GET /banking/reviews/{trace_id}`
- `GET /banking/reviews/search/by-risk`
- `POST /banking/reviews/{trace_id}/action`

### How to use each endpoint (Banking)
`GET /banking/health`
- Purpose: quick uptime check.

`POST /banking/rewrite`
- Purpose: rewrite a client email and get risk flags + disclaimer.
- Example body:
```json
{
  "email": "This product will give you excellent returns and is risk-free. You should buy today.",
  "audience": "client",
  "language": "en"
}
```

`GET /banking/reviews`
- Purpose: list recent audit records.
- Use it after running `/banking/rewrite` to see the latest items.

`GET /banking/reviews/{trace_id}`
- Purpose: fetch one audit record by trace ID.
- Use the `trace_id` returned from `/banking/rewrite`.

`GET /banking/reviews/search/by-risk?risk=high`
- Purpose: filter audit records by risk level.
- Example: `risk=high` or `risk=medium`.

`POST /banking/reviews/{trace_id}/action`
- Purpose: approve, reject, or edit a rewrite.
- Example body:
```json
{
  "action": "approve",
  "reviewer": "compliance.reviewer@company.com",
  "comment": "Approved for client communication."
}
```

Local (copy/paste):
```bash
curl -s http://localhost:8081/banking/health
curl -s http://localhost:8081/banking/rewrite \
  -H "Content-Type: application/json" \
  -d '{"email":"This product will give you excellent returns and is risk-free. You should buy today.","audience":"client","language":"en"}' | jq
```

Azure (copy/paste):
```bash
curl -i https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health
curl -s https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite \
  -H "Content-Type: application/json" \
  -d '{"email":"This product will give you excellent returns and is risk-free. You should buy today.","audience":"client","language":"en"}'
```

## Quickstart
Local run:
```bash
python -m uvicorn src.banking.app:app --reload --port 8081
```

Docker run:
```bash
docker run --rm -p 8081:80 mofasshara/pharma-email-assistant:banking-v4
```

Azure endpoints:
```text
https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health
https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite
```

Example curl flow:
```bash
curl -i https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health
curl -s -X POST https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite \
  -H "Content-Type: application/json" \
  -d '{"email":"This product will give you excellent returns and is risk-free. You should buy.","audience":"client","language":"en"}' | jq .
```

## Banking Risk Rewriter (What This Service Does)
- Rewrites client communication to reduce risky language
- Flags risky phrases
- Risk-level classification: low / medium / high
- Always adds disclaimer for audience=client|external

## Public Endpoints (Production URLs)
Health
```bash
curl -i https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health
```

Rewrite
```json
{
  "email": "string",
  "audience": "string",
  "language": "en"
}
```

## Banking End-to-End Flow (Copy/Paste)
```bash
# 1) Health check
curl -i https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health

# 2) Show banking endpoints exist
curl -s https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/openapi.json | grep -n "/banking"

# 3) Real rewrite request
curl -i -X POST \
  "https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"This product will give you excellent returns and is risk-free. You should buy today.",
    "audience":"client",
    "language":"en"
  }' | jq .

# 4) Fetch review by trace_id (if your system stores it)
curl -s https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/reviews/<TRACE_ID> | jq .
```

Example response (real):
```json
{
  "rewritten_email": "This product may give you excellent returns and is lower-risk. you may wish to buy today.\n\nDisclaimer: This message is for information purposes only and does not constitute investment advice. Any decision should be based on your risk profile and suitability assessment.",
  "risk_level": "high",
  "flagged_phrases": [
    "will give you excellent returns",
    "risk-free",
    "you should buy"
  ],
  "disclaimer_added": true,
  "rationale": "Detected 3 risky phrase(s). Risk classified as high. Added disclaimer."
}
```

## Architecture (Tiny but Clear)
FastAPI routes:
- /banking/health
- /banking/rewrite

Banking rewrite logic:
- src/banking/rewrite_service.py

Models:
- src/banking/schemas.py

Core logic:
- _find_flagged_phrases() -> flagged_phrases
- _risk_level() -> risk_level
- _rewrite_minimal() -> safe rewrite
- disclaimer appended for audience=client|external

## Build and Deploy (ARM Mac -> Azure amd64)
Build and push (Azure compatible):
```bash
docker buildx create --name mof-builder --use
docker buildx inspect --bootstrap

docker buildx build \
  --platform linux/amd64 \
  -t mofasshara/pharma-email-assistant:banking-v4 \
  --push .
```

Azure Container settings:
- Container type: Single container
- Registry: docker.io
- Image: mofasshara/pharma-email-assistant:banking-v4
- Startup command: `uvicorn src.banking.app:app --host 0.0.0.0 --port 80`
- Restart app after save

## Risk Classification: Fast Visible Value
- Reduces advisory language to "informational tone"
- Adds disclaimer automatically for external comms
- Produces explainable output: flagged_phrases + rationale

## End-to-End Banking Risk Flow
This section explains the full lifecycle of a banking-compliance rewrite request.
It demonstrates deterministic risk scoring, auditability, traceability, and
compliance workflows with API-driven review loops.

### 1) Client email -> POST /banking/rewrite
A client-facing employee sends an email to the API for rewriting and risk
evaluation.

Example request:
```bash
curl -s -X POST https://<your-app>.azurewebsites.net/banking/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "email": "This product will give you excellent returns and is risk-free. You should buy.",
    "audience": "client",
    "language": "en"
  }'
```

### 2) AI rewrite + deterministic risk rules applied
The system performs two things:

A) AI rewrite
- Improves tone
- Removes promotional or risky language
- Adds required disclaimers

B) Deterministic risk rules
These rules are not controlled by the LLM. They are policy-driven checks such as:
- "risk-free" -> high risk
- "guaranteed" -> high risk
- "excellent returns" -> medium/high
- "you should buy" -> high risk

Example response:
```json
{
  "rewritten_email": "Here is a more balanced explanation of the product...",
  "risk_level": "high",
  "flagged_phrases": [
    "excellent returns",
    "risk-free",
    "you should buy"
  ],
  "disclaimer_added": true,
  "rationale": "Detected 3 risky phrase(s) based on banking policy.",
  "trace_id": "b1c2d3e4-f567-8901-2345-6789abcdef01"
}
```

### 3) Audit event stored with trace_id
Every rewrite generates an audit record:
- original email
- rewritten email
- risk level
- flagged phrases
- timestamp
- tenant/domain context
- review status (pending/approved/rejected)

This is stored under the trace_id and supports compliance, investigations,
reproducibility, and regulatory audits.

### 4) Compliance retrieves review via /banking/reviews/{trace_id}
```bash
curl -s https://<your-app>.azurewebsites.net/banking/reviews/b1c2d3e4-f567-8901-2345-6789abcdef01 | jq .
```

Example review record:
```json
{
  "trace_id": "b1c2d3e4-f567-8901-2345-6789abcdef01",
  "original_email": "This product will give you excellent returns...",
  "rewritten_email": "Here is a more balanced explanation...",
  "risk_level": "high",
  "flagged_phrases": [
    "excellent returns",
    "risk-free",
    "you should buy"
  ],
  "review_status": "pending",
  "timestamp": "2025-01-12T14:32:10Z"
}
```

### 5) High-risk items flagged for manual review
If the risk level is "high":
- The item is marked for manual review
- Compliance can approve, reject, or request edits via:
  - `POST /banking/reviews/{trace_id}/action`

### Why this matters (Tech Lead explanation)
- Auditability: every rewrite is traceable via trace_id
- Deterministic risk scoring: policy-driven, predictable, testable, and versionable
- Separation of concerns: rewrite, risk, and audit logic are decoupled
- Compliance workflow: high-risk items move through a review pipeline
- Production-grade architecture: clear, structured, operational docs

## Platform Architecture
This system separates:
- Platform concerns (policy, audit, runtime context)
- Domain logic (banking, pharma)

This enables:
- Regulated deployments
- Domain-specific rules without code duplication
- Auditability and explainability

Flow:
Request
  -> Runtime Context
  -> Policy Loader
  -> Deterministic Risk Layer
  -> LLM (optional)
  -> Audit Log
  -> Response

## Banking Risk Rewriter — Review Workflow (Human-in-the-loop)
Endpoints

GET /banking/health

POST /banking/rewrite

GET /banking/reviews (lists recent audit items)

GET /banking/reviews/{trace_id} (fetch one audit item)

POST /banking/reviews/{trace_id}/action (approve / reject / edit)

Response fields (important)

Every rewrite returns:
- trace_id — unique id used for audit + review
- created_at — timestamp (UTC ISO)
- review_status — pending | approve | reject | edit

Explanation: This is the “audit handle” a bank would require.

### Base URLs
Local
- API docs: http://localhost:8081/docs
- Base: http://localhost:8081

Azure
- Base: https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net

Tip: Replace <BASE_URL> in the examples below with either Local or Azure.

### Full Example Flow (cURL) — Rewrite → Review → Approve/Edit/Reject
Step 0 — Pick your base URL

Local
```bash
export BASE_URL="http://localhost:8081"
```

Azure
```bash
export BASE_URL="https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net"
```

Step 1 — Health check (sanity)
```bash
curl -i "$BASE_URL/banking/health"
```

Expected: 200 OK with something like:
```json
{"status":"ok","service":"banking-risk-rewriter"}
```

Step 2 — POST a rewrite request

Your current request schema is:
```json
{
  "email": "string",
  "audience": "string",
  "language": "en"
}
```

Run:
```bash
curl -s -X POST "$BASE_URL/banking/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "This product will give you excellent returns, it is risk-free, and you should buy today.",
    "audience": "client",
    "language": "en"
  }' | tee /tmp/banking_rewrite_response.json
```

What this does:
- Sends a risky banking email
- Saves the JSON response to /tmp/banking_rewrite_response.json

Step 3 — Extract the trace_id

Option A (recommended) — with jq
```bash
TRACE_ID=$(cat /tmp/banking_rewrite_response.json | jq -r '.trace_id')
echo "TRACE_ID=$TRACE_ID"
```

Option B — no jq
```bash
TRACE_ID=$(python -c "import json; print(json.load(open('/tmp/banking_rewrite_response.json'))['trace_id'])")
echo "TRACE_ID=$TRACE_ID"
```

Expected: prints something like:
```
TRACE_ID=2b5c7d0a-...-...
```

Step 4 — List recent reviews (audit queue)
```bash
curl -s "$BASE_URL/banking/reviews?limit=10" | tee /tmp/banking_reviews_list.json
```

Expected:
- A list of items including your trace_id
- review_status should be "pending" initially

Step 5 — Fetch the audit item by trace_id
```bash
curl -s "$BASE_URL/banking/reviews/$TRACE_ID" | tee /tmp/banking_review_item.json
```

Expected:
- Contains request + response
- Includes trace_id, created_at, review_status

### Review Actions — Approve / Reject / Edit
A) Approve
```bash
curl -s -X POST "$BASE_URL/banking/reviews/$TRACE_ID/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "reviewer": "compliance.reviewer@company.com",
    "comment": "Approved for client communication."
  }'
```

Then verify:
```bash
curl -s "$BASE_URL/banking/reviews/$TRACE_ID" | jq '.review_status'
```

Expected: "approve"

B) Reject

Run a new rewrite first (to get a new trace_id), then:
```bash
curl -s -X POST "$BASE_URL/banking/reviews/$TRACE_ID/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "reviewer": "compliance.reviewer@company.com",
    "comment": "Still contains advisory language; do not send."
  }'
```

Verify:
```bash
curl -s "$BASE_URL/banking/reviews/$TRACE_ID" | jq '.review_status'
```

Expected: "reject"

C) Edit (human corrects the output)
```bash
curl -s -X POST "$BASE_URL/banking/reviews/$TRACE_ID/action" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "edit",
    "reviewer": "compliance.reviewer@company.com",
    "comment": "Adjusted language to remove implied recommendation.",
    "edited_email": "This product may be suitable depending on your objectives and risk tolerance. Please review the product documentation and consider whether it aligns with your risk profile.\n\nDisclaimer: This message is for information purposes only and does not constitute investment advice. Any decision should be based on your risk profile and suitability assessment."
  }'
```

Verify:
```bash
curl -s "$BASE_URL/banking/reviews/$TRACE_ID" | jq '.review_status, .response.rewritten_email // .rewritten_email'
```

Expected:
- status: "edit"
- rewritten text updated to your edited email

### Same Flow in Swagger UI (Click-by-click)
Open:
- Local: http://localhost:8081/docs
- Azure: https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/docs

Expand Banking tag

Run POST /banking/rewrite

Copy trace_id from response

Run GET /banking/reviews

Run GET /banking/reviews/{trace_id}

Run POST /banking/reviews/{trace_id}/action with:
- approve or reject or edit

### JSON structure notes
Your rewrite response includes:
- rewritten_email, risk_level, flagged_phrases, disclaimer_added, rationale
- trace_id, created_at, review_status

If your audit endpoint returns a wrapper like:
```json
{
  "trace_id": "...",
  "request": {...},
  "response": {...},
  "review_status": "pending"
}
```
then the jq lines referencing `.response.rewritten_email` will work.
If instead it returns only the response shape, use `.rewritten_email`.

## Live endpoints (Azure)
- Health: `GET /banking/health`
- Rewrite: `POST /banking/rewrite`
- OpenAPI: `/docs` and `/openapi.json`

Example:
- `https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health`

## API schema
### POST /banking/rewrite
Request body:
```json
{
  "email": "string",
  "audience": "string",
  "language": "en"
}
```

Response body:
```json
{
  "rewritten_email": "string",
  "risk_level": "medium",
  "flagged_phrases": ["string"],
  "disclaimer_added": true,
  "rationale": "string"
}
```

Quick test (curl)

Health:
```bash
curl -i "https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/health"
```

Rewrite:
```bash
curl -i -X POST \
  "https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite" \
  -H "Content-Type: application/json" \
  -d '{"email":"This product will give you excellent returns. You should invest now.","audience":"client","language":"en"}'
```

Local dev (Docker)

Build:
```bash
docker build -t pharma-email-assistant:local .
```

Run:
```bash
docker run --rm -p 8081:80 \
  pharma-email-assistant:local
```

Test locally:
```bash
curl -i http://localhost:8081/banking/health
```

ARM Mac + Azure (AMD64) build

If you're on an ARM64 Mac, build an AMD64 image for Azure:
```bash
docker buildx create --use --name multiarch || docker buildx use multiarch
docker buildx build --platform linux/amd64 \
  -t mofasshara/pharma-email-assistant:banking-v4 \
  --push .
```

Risk classification rules (current)

Document what you’re flagging (examples):
- "guaranteed returns" -> high
- "will give you excellent returns" -> medium
- "you should invest now" -> medium/high

Notes

This is a demo for internal pilot-style workflows:
- human-in-the-loop friendly outputs
- audit-friendly rationale
- deterministic response schema

## Architecture (high level)
Client -> FastAPI (`/banking/rewrite`)
-> risk phrase scan + risk level assignment
-> disclaimer injection (if needed)
-> rewrite (rule-based rewrite v1)
-> structured JSON response + request id

## Azure App Service (container) settings
- Container type: Single container
- Registry: docker.io
- Image: mofasshara/pharma-email-assistant:banking-v4
- Startup command: `uvicorn src.banking.app:app --host 0.0.0.0 --port 80`
- Port: 80 (via WEBSITES_PORT)

# pharma-email-assistant2
AI-powered email rewriting assistant for medical/pharma use cases.
![Architecture Diagram](Untitled-2025-12-11-1423.png)

## Roadmap (Upcoming Weeks)
- Audience-specific rewriting prompts
- Compliance checker agent
- Add hallucination evaluation
- Add Docker deployment to Azure
## System Architecture
![architecture](docs/architecture.png)
## How logging works
- Every request to the `/rewrite` endpoint is recorded using Loguru.
- Logs include: input text, audience type, output email, and timestamp.
- Sensitive data (names, IDs, emails) should be anonymized before saving.
- Logs are stored in `logs/requests.jsonl` for later review.

## How to submit feedback
- After testing a rewritten email, you can rate or comment on its quality.
- Feedback is captured via the `/feedback` endpoint (to be added in Week 3).
- Each feedback entry links to the original request and output.
- This helps identify strong examples for fine-tuning and weak ones to improve.

## How to export dataset for evaluation
- Logged requests and feedback can be exported into a dataset file.
- Example: run a script that reads `logs/requests.jsonl` and outputs `dataset.csv`.
- The dataset includes: input, audience, output, feedback, and compliance tags.
- This dataset is then used for evaluation or fine-tuning in Month 3.

# Pharma Email Assistant

A FastAPI-based application that rewrites pharma-related emails using OpenAI models.  
Deployed on Azure App Service with Docker.

## Quick User Guide (Pharma)
1) Open: https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/docs
2) Click **POST /rewrite** → **Try it out**.
3) Paste a body and click **Execute**.

Example:
```json
{
  "text": "This product guarantees the best patient outcomes.",
  "audience": "medical affairs"
}
```

## Pharma Email Rewriter (How it works)
1) Receive request at `POST /rewrite` with `text` and `audience`.
2) Run safety checks on the input.
3) Rewrite the email using the pharma prompt for the audience.
4) Run safety checks on the output.
5) Log the request/output for evaluation.
6) Return the rewritten email (or an error if blocked).

## Pharma API (How to use each endpoint)
`GET /`
- Purpose: quick uptime check.

`POST /rewrite`
- Purpose: rewrite a pharma email using the audience-specific prompt.
- Example body:
```json
{
  "text": "This product guarantees the best patient outcomes.",
  "audience": "medical affairs"
}
```

`POST /feedback`
- Purpose: submit a rating and comments on a rewrite.
- Example body:
```json
{
  "input_text": "This product guarantees the best patient outcomes.",
  "audience": "medical affairs",
  "output": {"rewritten_email": "Example output..."},
  "rating": 5,
  "comments": "Clear and compliant."
}
```

---

## 🚀 Live Demo
- API Docs: https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/docs

---

## 🏗️ Deployment Architecture
- **Frontend**: Swagger UI (auto-generated by FastAPI)
- **Backend**: FastAPI app (`src/api/main.py`)
- **Containerization**: Docker (Python 3.10-slim base image)
- **Hosting**: Azure App Service (Linux, B1 plan)
- **Registry**: Docker Hub (`mofasshara/pharma-email-assistant:rewrite`)

Flow:
1. Code → Docker build → Push to Docker Hub  
2. Azure App Service pulls image → Runs container on port 80  
3. Public endpoint exposed via `azurewebsites.net`

---

## 🔑 Environment Variable Setup
Configured in **Azure Portal → Settings → Environment Variables**:

| Name            | Value Example           | Purpose                          |
|-----------------|-------------------------|----------------------------------|
| `OPENAI_API_KEY`| `sk-xxxxxx`             | Authenticates with OpenAI API    |
| `OPENAI_MODEL`  | `gpt-4o-mini`           | Defines model used for rewriting |

Secrets are **never hardcoded** in code — they are injected at runtime by Azure.

---

## ☁️ Azure App Service Explanation
- **App Service Plan**: B1 (Basic, Linux) — beginner-friendly, cost-effective  
- **Continuous Deployment**: Pulls latest Docker image from Docker Hub  
- **Scaling**: Can scale vertically (larger plan) or horizontally (multiple instances)  
- **Monitoring**: Log Stream + Health Check for uptime visibility  
- **Security**: Environment variables stored securely, HTTPS enabled by default  

---

## 📌 Next Steps
- Add `/health` endpoint for monitoring  
- Configure CI/CD with GitHub Actions → auto-build & push Docker image  
- Document usage examples in README (sample payloads for `/rewrite`)  

## 🖼️ Screenshots

### Azure Web App overview
"C:\Users\mofas\OneDrive\Desktop\AI engineer\docs.azure-app-overview.png"

### Swagger UI (live)
"C:\Users\mofas\OneDrive\Desktop\AI engineer\fastapi.UI.png"

## Live Deployments (Azure)

- Agent Orchestrator API (FastAPI + LangChain):  
  https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/docs

- Banking Risk Rewriter API (FastAPI):  
  https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/docs

- Pharma Email Rewriter API (FastAPI):  
  https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/docs

- RAG Service API (FastAPI):  
  https://rag-mofr-fhhseqb2c0etaeh9.westeurope-01.azurewebsites.net/docs

### Architecture
Agent Orchestrator routes requests and calls downstream tool services via environment-configured URLs.

## Production Architecture

- Agent API (FastAPI) deployed on Azure App Service
- Rewrite LLM service deployed as separate App Service
- RAG service deployed as separate App Service
- Agent orchestrates calls to rewrite service via HTTP
- Hardened with:
  - HTTPS normalization
  - Request timeouts
  - Clear error propagation
- Observability:
  - Azure Log Stream
  - Application Insights (Search, Failures)
  - Availability monitoring
    
## Reliability & Monitoring

- Health endpoints for all services
- Azure Application Insights for:
  - Request tracing
  - Failure analysis
- Availability tests with alerting enabled
- Defensive networking (timeouts, retries, URL validation)
