from fastapi import APIRouter, HTTPException

from src.banking.schemas import (
    BankingRewriteRequest,
    BankingRewriteResponse,
    ReviewActionRequest,
)
from src.banking.rewrite_service import rewrite_banking_email
from src.banking.audit_store import append_record, append_review_event, get_record, list_records

router = APIRouter(prefix="/banking", tags=["banking"])


@router.get("/health")
def banking_health():
    return {"status": "ok", "service": "banking-risk-rewriter"}


@router.post("/rewrite", response_model=BankingRewriteResponse)
def banking_rewrite(req: BankingRewriteRequest):
    try:
        return rewrite_banking_email(req)
    except Exception:
        raise HTTPException(status_code=500, detail="Banking rewrite failed")


@router.get("/reviews")
def banking_reviews(limit: int = 50):
    return {"items": list_records(limit=limit)}


@router.get("/reviews/{trace_id}")
def banking_review(trace_id: str):
    record = get_record(trace_id)
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    return record


@router.post("/reviews/{trace_id}/action")
def banking_review_action(trace_id: str, payload: ReviewActionRequest):
    record = get_record(trace_id)
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")

    if payload.action == "edit" and not payload.edited_email:
        raise HTTPException(status_code=400, detail="edited_email required for edit")

    response = record.get("response", {})
    response["review_status"] = payload.action
    if payload.action == "edit":
        response["rewritten_email"] = payload.edited_email

    record["review_status"] = payload.action
    record["response"] = response
    append_record(record)

    review_event = {
        "trace_id": trace_id,
        "action": payload.action,
        "reviewer": payload.reviewer,
        "comment": payload.comment,
        "edited_email": payload.edited_email,
    }
    append_review_event(review_event)
    return {"status": "ok", "trace_id": trace_id, "review_status": payload.action}
