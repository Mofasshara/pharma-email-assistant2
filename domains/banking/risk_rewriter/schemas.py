from pydantic import BaseModel, Field
from typing import List, Literal

RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class BankingRewriteRequest(BaseModel):
    text: str = Field(..., min_length=10)
    audience: str = Field(default="Client")


class BankingRewriteResponse(BaseModel):
    rewritten_text: str
    risk_level: RiskLevel
    flags: List[str] = []
    disclaimer_added: bool = False
    explanation: str
    trace_id: str
