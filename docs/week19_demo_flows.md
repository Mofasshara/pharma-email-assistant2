# Demo Flows (copy/paste for interviews)

## Flow A — Banking: rewrite + risk + disclaimer + review lookup

### 1) Rewrite request
```bash
curl -i -X POST \
  "https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "This product will give you excellent returns and is risk-free. You should buy.",
    "audience": "client",
    "language": "en"
  }'
```

Example response:
```json
{
  "rewritten_email": "This product may give you excellent returns and is lower-risk. you may wish to buy.\n\nDisclaimer: This message is for information purposes only and does not constitute investment advice. Any decision should be based on your risk profile and suitability assessment.\n",
  "risk_level": "high",
  "flagged_phrases": [
    "risk-free",
    "will give you excellent returns",
    "you should buy"
  ],
  "disclaimer_added": true,
  "trace_id": "e5492f65-e3fd-4ae3-b0fc-4295bf76cf00",
  "created_at": "2025-12-23T00:34:49.360196Z",
  "review_status": "pending",
  "rationale": "Detected 3 risky phrase(s). Risk classified as high. Added disclaimer."
}
```

### 2) Review lookup by trace_id
```bash
curl -s \
  "https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/banking/reviews/e5492f65-e3fd-4ae3-b0fc-4295bf76cf00" \
  | jq .
```

Where to get the trace_id:
- Use the `trace_id` field returned by the `POST /banking/rewrite` response.

## Flow B — Pharma: rewrite flow

### 1) Rewrite request
```bash
curl -i -X POST \
  "https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Please send the updated protocol draft for review.",
    "audience": "medical affairs"
  }'
```

Example response:
```json
{
  "rewritten_email": "Subject: Protocol Draft Review\n\nDear Team,\n\nPlease send the updated protocol draft for review at your earliest convenience.\n\nBest regards,\n[Your Name]",
  "metadata": {
    "model": "gpt-4o-mini"
  }
}
```

## Flow C — Orchestrator: route request to the right domain

### 1) Route to Pharma via orchestrator
```bash
curl -i -X POST \
  "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/agent/handle" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Please send the updated protocol draft for review.",
    "audience": "medical affairs",
    "domain": "pharma"
  }'
```

Example response:
```json
{
  "domain": "pharma",
  "response": {
    "rewritten_email": "Subject: Protocol Draft Review\n\nDear Team,\n\nPlease send the updated protocol draft for review at your earliest convenience.\n\nBest regards,\n[Your Name]",
    "metadata": {
      "model": "gpt-4o-mini"
    }
  },
  "request_id": "1744716d-72e0-4186-a2f4-b5cb72fe671c"
}
```

### 2) Route to Banking via orchestrator
```bash
curl -i -X POST \
  "https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/agent/handle" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "This product will give you excellent returns and is risk-free.",
    "audience": "client",
    "domain": "banking"
  }'
```

Example response:
```json
{
  "domain": "banking",
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
