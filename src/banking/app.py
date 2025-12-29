from fastapi import FastAPI

from src.banking.api import router as banking_router

app = FastAPI(
    title="Banking Risk Rewriter API",
    description=(
        "<details><summary>Quick User Guide (click to expand)</summary>\n\n"
        "**Purpose:** Rewrite banking emails to reduce compliance risk and add disclaimers.\n\n"
        "**How to use:**\n"
        "1) Open `/docs` and expand `POST /banking/rewrite`.\n"
        "2) Paste the request body and click **Execute**.\n"
        "3) Copy the `trace_id` to review the audit record.\n"
        "</details>"
    ),
)
app.include_router(banking_router)
