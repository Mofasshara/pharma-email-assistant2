# Ops Readiness Checklist (Week 19)

## Health checks (confirmed in README)
- Banking: `/banking/health`
- Pharma: `/` (health endpoint for the pharma rewrite service)
- Orchestrator: `/agent/health`
- RAG: `/rag/health`

## Key settings (names only)
### Banking app (banking-risk-rewriter-mofr)
- `WEBSITES_PORT`
- `WEBSITE_HEALTHCHECK_MAXPINGFAILURES`
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE`

### Orchestrator app (pharma-email-assistant-mofr)
- `BANKING_API_BASE`
- `REWRITE_API_BASE`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `LOG_LEVEL`
- `STARTUP_COMMAND`
- `WEBSITE_HEALTHCHECK_MAXPINGFAILURES`
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE`

### Pharma app (pharma-email-rewrite-mofr)
- `OPENAI_API_KEY`
- `WEBSITE_HEALTHCHECK_MAXPINGFAILURES`
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE`

### RAG app (rag-mofr-fhhseqb2c0etaeh9)
- `OPENAI_API_KEY`
- `WEBSITES_PORT`
- `WEBSITE_HEALTHCHECK_MAXPINGFAILURES`
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE`

## What I’d alert on
- Health check failures per service
- Latency spikes from orchestrator to downstream
- Sustained 5xx rates per domain
- Sudden traffic drops
- Unexpected error type changes

## Log stream confirmation (signal only)
- Banking: log stream shows `GET /banking/health` returning 200
- Pharma: log stream shows `GET /` returning 200
- Orchestrator: log stream shows `GET /agent/health` returning 200
- RAG: log stream shows `GET /rag/health` returning 200
