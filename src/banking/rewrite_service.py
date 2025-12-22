import re
from typing import List

from src.banking.schemas import BankingRewriteRequest, BankingRewriteResponse

RISKY_PHRASES = [
    "guaranteed returns",
    "will give you excellent returns",
    "risk-free",
    "no risk",
    "you should buy",
    "i recommend you invest",
]

DISCLAIMER = (
    "\n\nDisclaimer: This message is for information purposes only and does not "
    "constitute investment advice. Any decision should be based on your risk "
    "profile and suitability assessment."
)


def _find_flagged_phrases(text: str) -> List[str]:
    lowered = text.lower()
    found = []
    for phrase in RISKY_PHRASES:
        if phrase in lowered:
            found.append(phrase)
    return found


def _risk_level(found: List[str]) -> str:
    if not found:
        return "low"
    if len(found) <= 2:
        return "medium"
    return "high"


def _rewrite_minimal(email: str) -> str:
    # Minimal safe rewrite: remove strong advisory language patterns
    replacements = [
        (r"\bwill\b", "may"),
        (r"\bguaranteed\b", "potential"),
        (r"\brisk[- ]free\b", "lower-risk"),
        (r"\byou should\b", "you may wish to"),
        (r"\bi recommend\b", "it may be appropriate to consider"),
    ]
    out = email
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out.strip()


def rewrite_banking_email(req: BankingRewriteRequest) -> BankingRewriteResponse:
    flagged = _find_flagged_phrases(req.email)
    risk = _risk_level(flagged)

    rewritten = _rewrite_minimal(req.email)

    # Always append disclaimer for client-facing messages
    disclaimer_added = True
    if req.audience.lower() in {"client", "external"}:
        if DISCLAIMER not in rewritten:
            rewritten = rewritten + DISCLAIMER
    else:
        # internal emails may not need disclaimer
        disclaimer_added = False

    disclaimer_note = (
        "Added disclaimer."
        if disclaimer_added
        else "No disclaimer for internal audience."
    )
    rationale = (
        f"Detected {len(flagged)} risky phrase(s). "
        f"Risk classified as {risk}. "
        f"{disclaimer_note}"
    )

    return BankingRewriteResponse(
        rewritten_email=rewritten,
        risk_level=risk,
        flagged_phrases=flagged,
        disclaimer_added=disclaimer_added,
        rationale=rationale,
    )
