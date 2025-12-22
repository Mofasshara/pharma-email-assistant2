from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

router = APIRouter(prefix="/banking", tags=["banking"])


class BankingRewriteRequest(BaseModel):
    email: str = Field(..., min_length=10, description="Raw client email text")
    audience: Literal["client", "internal", "compliance"] = "client"
    risk_level: Literal["low", "medium", "high"] = "medium"


class BankingRewriteResponse(BaseModel):
    rewritten_email: str
    risk_flags: list[str]
    disclaimer_added: bool


@router.get("/health")
def health():
    return {"status": "ok", "service": "banking-risk-rewriter"}


@router.post("/rewrite", response_model=BankingRewriteResponse)
def rewrite(req: BankingRewriteRequest):
    """
    Banking risk rewriter:
    - removes advisory/guaranteed-return language
    - injects disclaimers
    - flags risky phrases
    """
    try:
        # TODO: Replace this with your real LLM/service call
        risky_phrases = [
            "guaranteed",
            "excellent returns",
            "no risk",
            "will outperform",
        ]
        found = [p for p in risky_phrases if p.lower() in req.email.lower()]

        disclaimer = (
            "\n\nDisclaimer: This message is for information only and does not "
            "constitute investment advice."
        )

        rewritten = req.email.strip()

        # Simple placeholder rewrite logic (replace later with LLM prompt)
        rewritten = rewritten.replace("guaranteed", "may")
        rewritten = rewritten.replace("excellent returns", "potential returns")

        disclaimer_added = False
        if req.risk_level in ("medium", "high"):
            rewritten = rewritten + disclaimer
            disclaimer_added = True

        return BankingRewriteResponse(
            rewritten_email=rewritten,
            risk_flags=found,
            disclaimer_added=disclaimer_added,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Banking rewrite failed: {e}")
