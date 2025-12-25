from pydantic import BaseModel
from typing import List


class BankingReviewResponse(BaseModel):
    trace_id: str
    original_email: str
    rewritten_email: str
    risk_level: str
    flagged_phrases: List[str]
    disclaimer_added: bool
    review_notes: str
    compliance_status: str  # "pass" | "review" | "fail"
