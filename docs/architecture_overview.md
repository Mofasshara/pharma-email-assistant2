# Platform Architecture Overview

Client
  |
  +--> Agent Orchestrator (Azure App Service)
  |       |
  |       |-- routes --> Banking Risk Rewriter (Azure App Service)
  |       |
  |       |-- routes --> Pharma Rewrite (Azure App Service)
  |       |
  |       |-- uses --> RAG Service (Azure App Service)
  |
  +--> Banking Risk Rewriter (Azure App Service) [direct]
  |
  +--> Pharma Rewrite (Azure App Service) [direct]
  |
  +--> RAG Service (Azure App Service) [direct]

- Orchestrator = routing + safety boundary
- Domain services = business logic only
- RAG Service = document retrieval and grounded answers
- Independent deployability (4 separate apps)

## Live URLs (4 apps)
- Orchestrator: https://pharma-email-assistant-mofr-gzcfdrhwgrdqgdgd.westeurope-01.azurewebsites.net/docs
- Banking: https://banking-risk-rewriter-mofr-bqe6akf3bwbzenfb.westeurope-01.azurewebsites.net/docs
- Pharma: https://pharma-email-rewrite-mofr-gph0dueeegetf9gr.westeurope-01.azurewebsites.net/docs
- RAG: https://rag-mofr-fhhseqb2c0etaeh9.westeurope-01.azurewebsites.net/docs
