from pydantic import BaseModel, Field
from typing import List, Optional


class BankingRewriteRequest(BaseModel):
    email: str = Field(..., min_length=1)
    audience: str = Field(..., min_length=1)  # e.g. "client", "internal"
    language: str = "en"


class BankingRewriteResponse(BaseModel):
    rewritten_email: str
    risk_level: str  # "low" | "medium" | "high"
    flagged_phrases: List[str] = []
    disclaimer_added: bool = True
    rationale: Optional[str] = None
