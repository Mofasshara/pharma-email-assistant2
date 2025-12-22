# Banking Client Communication Risk Rewriter (FINMA-style guardrails)

A FastAPI service that rewrites relationship-manager emails to reduce regulatory/compliance risk.
It classifies risk level, flags risky phrases, and injects a disclaimer when needed.

## What it does
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

## Banking API
What it does:
- Rewrites client-facing drafts to remove risky language.
- Flags risky phrases and adds a disclaimer when needed.

Why banks care:
- Compliance-safe rewriting and audit-friendly rationale.

Endpoints:
- `GET /banking/health`
- `POST /banking/rewrite`

Local (copy/paste):
```bash
curl -s http://localhost:8081/banking/health
curl -s http://localhost:8081/banking/rewrite \
  -H "Content-Type: application/json" \
  -d '{"email":"This product will give you excellent returns and is risk-free. You should buy today.","audience":"client","language":"en"}' | jq
```

Azure (copy/paste):
```bash
curl -i https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/health
curl -s https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/rewrite \
  -H "Content-Type: application/json" \
  -d '{"email":"This product will give you excellent returns and is risk-free. You should buy today.","audience":"client","language":"en"}'
```

## Quickstart
Local run:
```bash
python -m uvicorn agents.api:app --reload --port 8081
```

Docker run:
```bash
docker run --rm -p 8081:80 mofasshara/pharma-email-assistant:banking-v2
```

Azure endpoints:
```text
https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/health
https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/rewrite
```

Example curl flow:
```bash
curl -i https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/health
curl -s -X POST https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/rewrite \
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
curl -i https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/health
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
curl -i https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/health

# 2) Show banking endpoints exist
curl -s https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/openapi.json | grep -n "/banking"

# 3) Real rewrite request
curl -i -X POST \
  "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"This product will give you excellent returns and is risk-free. You should buy today.",
    "audience":"client",
    "language":"en"
  }' | jq .

# 4) Fetch review by trace_id (if your system stores it)
curl -s https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/reviews/<TRACE_ID> | jq .
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
  -t mofasshara/pharma-email-assistant:banking-v2 \
  --push .
```

Azure Container settings:
- Container type: Single container
- Registry: docker.io
- Image: mofasshara/pharma-email-assistant:banking-v2
- Startup command: (blank)
- Restart app after save

## Risk Classification: Fast Visible Value
- Reduces advisory language to "informational tone"
- Adds disclaimer automatically for external comms
- Produces explainable output: flagged_phrases + rationale

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
- Base: https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net

Tip: Replace <BASE_URL> in the examples below with either Local or Azure.

### Full Example Flow (cURL) — Rewrite → Review → Approve/Edit/Reject
Step 0 — Pick your base URL

Local
```bash
export BASE_URL="http://localhost:8081"
```

Azure
```bash
export BASE_URL="https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net"
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
- Azure: https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/docs

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
- `https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/health`

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
curl -i "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/health"
```

Rewrite:
```bash
curl -i -X POST \
  "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/banking/rewrite" \
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
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  pharma-email-assistant:local
```

Test locally:
```bash
curl -i http://localhost:8080/banking/health
```

ARM Mac + Azure (AMD64) build

If you're on an ARM64 Mac, build an AMD64 image for Azure:
```bash
docker buildx create --use --name multiarch || docker buildx use multiarch
docker buildx build --platform linux/amd64 \
  -t mofasshara/pharma-email-assistant:banking-v2 \
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
- Image: mofasshara/pharma-email-assistant:banking-v2
- Port: 8080 (via PORT env var, if used)

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

- # Pharma Email Assistant

A FastAPI-based application that rewrites pharma-related emails using OpenAI models.  
Deployed on Azure App Service with Docker.

---

## 🚀 Live Demo
- API Docs: https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/docs

---

## 🏗️ Deployment Architecture
- **Frontend**: Swagger UI (auto-generated by FastAPI)
- **Backend**: FastAPI app (`src/api/main.py`)
- **Containerization**: Docker (Python 3.10-slim base image)
- **Hosting**: Azure App Service (Linux, B1 plan)
- **Registry**: Docker Hub (`mofasshara/pharma-email-assistant:latest`)

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

- Rewrite Service API (FastAPI):  
  https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/docs

### Architecture
Agent Orchestrator routes requests and calls downstream tool services via environment-configured URLs.

## Production Architecture

- Agent API (FastAPI) deployed on Azure App Service
- Rewrite LLM service deployed as separate App Service
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
