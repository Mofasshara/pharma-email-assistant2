from pydantic import BaseModel, Field
from typing import List, Literal, Optional

RiskLevel = Literal["low", "medium", "high"]


class BankingRewriteRequest(BaseModel):
    email: str = Field(..., min_length=10)
    audience: Literal["client", "internal", "external"]
    language: str = "en"


class BankingRewriteResponse(BaseModel):
    rewritten_email: str
    risk_level: RiskLevel
    flagged_phrases: List[str] = []
    disclaimer_added: bool = True
    trace_id: str
    created_at: str
    review_status: str = "pending"
    rationale: Optional[str] = None


class ReviewActionRequest(BaseModel):
    action: Literal["approve", "reject", "edit"]
    reviewer: str
    comment: Optional[str] = None
    edited_email: Optional[str] = None
