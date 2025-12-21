from fastapi import APIRouter, HTTPException

from domains.banking.risk_rewriter.schemas import (
    BankingRewriteRequest,
    BankingRewriteResponse,
)
from domains.banking.risk_rewriter.service import banking_risk_rewrite

router = APIRouter(prefix="/banking", tags=["Banking"])


@router.post("/rewrite", response_model=BankingRewriteResponse)
def rewrite(req: BankingRewriteRequest):
    try:
        out = banking_risk_rewrite(req.text, req.audience)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
