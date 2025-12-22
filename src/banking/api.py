from fastapi import APIRouter

from src.banking.schemas import BankingRewriteRequest, BankingRewriteResponse
from src.banking.rewrite_service import rewrite_banking_email

router = APIRouter(prefix="/banking", tags=["banking"])


@router.get("/health")
def banking_health():
    return {"status": "ok", "service": "banking-risk-rewriter"}


@router.post("/rewrite", response_model=BankingRewriteResponse)
def banking_rewrite(req: BankingRewriteRequest):
    return rewrite_banking_email(req)
