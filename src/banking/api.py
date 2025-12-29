from fastapi import APIRouter, HTTPException

from src.banking.schemas import (
    BankingRewriteRequest,
    BankingRewriteResponse,
    ReviewActionRequest,
)
from src.banking.rewrite_service import rewrite_banking_email
from src.banking.audit_store import (
    append_record,
    append_review_event,
    get_record,
    list_records,
    search_records_by_risk,
)
from platform_layer.runtime.context import RuntimeContext

router = APIRouter(prefix="/banking", tags=["banking"])


@router.get(
    "/health",
    description="Health check for the banking rewrite service.",
)
def banking_health():
    return {"status": "ok", "service": "banking-risk-rewriter"}


@router.post(
    "/rewrite",
    response_model=BankingRewriteResponse,
    description=(
        "Rewrite a client email and return risk flags + disclaimer status.\n\n"
        "**Example:**\n"
        "```json\n"
        "{\n"
        "  \"email\": \"This product will give you excellent returns and is risk-free. You should buy today.\",\n"
        "  \"audience\": \"client\",\n"
        "  \"language\": \"en\"\n"
        "}\n"
        "```"
    ),
)
def banking_rewrite(req: BankingRewriteRequest):
    try:
        ctx = RuntimeContext(
            domain="banking",
            audience=req.audience,
            language=req.language,
        )
        return rewrite_banking_email(req, ctx)
    except Exception:
        raise HTTPException(status_code=500, detail="Banking rewrite failed")


@router.get(
    "/reviews",
    description="List recent audit records.",
)
def banking_reviews(limit: int = 50):
    return {"items": list_records(limit=limit)}


@router.get(
    "/reviews/{trace_id}",
    description="Fetch a single audit record by trace_id.",
)
def banking_review(trace_id: str):
    record = get_record(trace_id)
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    return record


@router.get(
    "/reviews/search/by-risk",
    description="Filter audit records by risk level (low/medium/high).",
)
def banking_reviews_by_risk(risk: str):
    return {"items": search_records_by_risk(risk)}


@router.post(
    "/reviews/{trace_id}/action",
    description=(
        "Approve, reject, or edit a rewrite.\n\n"
        "**Approve example:**\n"
        "```json\n"
        "{\n"
        "  \"action\": \"approve\",\n"
        "  \"reviewer\": \"compliance.reviewer@company.com\",\n"
        "  \"comment\": \"Approved for client communication.\"\n"
        "}\n"
        "```"
    ),
)
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
