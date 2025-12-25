from fastapi import APIRouter, HTTPException

from domains.banking.review_service.service import load_by_trace_id, search_reviews
from domains.banking.review_service.schemas import BankingReviewResponse

router = APIRouter(prefix="/banking/reviews", tags=["Banking Reviews"])


@router.get("/{trace_id}", response_model=BankingReviewResponse)
def review(trace_id: str):
    event = load_by_trace_id(trace_id)
    if not event:
        raise HTTPException(404, "Trace not found")

    compliance = "pass" if event["risk_level"] == "low" else "review"

    return {
        **event,
        "review_notes": "Auto-reviewed based on risk rules.",
        "compliance_status": compliance,
    }


@router.get("/search/by-risk")
def search(risk: str):
    return {"items": search_reviews(risk)}
