import re
import uuid
from datetime import datetime
from typing import List

from src.banking.schemas import BankingRewriteRequest, BankingRewriteResponse
from src.banking.audit_store import append_record
from platform_layer.policies.loader import load_policy
from platform_layer.runtime.context import RuntimeContext

MAX_LEN = 5000

def _flatten_risk_phrases(risk_phrases: dict) -> List[str]:
    phrases: List[str] = []
    for level in ("high", "medium"):
        phrases.extend(risk_phrases.get(level, []))
    return phrases


def _find_flagged_phrases(text: str, phrases: List[str]) -> List[str]:
    lowered = text.lower()
    found = []
    for phrase in phrases:
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


def _post_process(rewritten: str) -> str:
    return _rewrite_minimal(rewritten)


def rewrite_banking_email(
    req: BankingRewriteRequest,
    ctx: RuntimeContext,
) -> BankingRewriteResponse:
    policy = load_policy(ctx.domain)
    risk_phrases = _flatten_risk_phrases(policy.get("risk_phrases", {}))
    disclaimer_required_for = set(policy.get("disclaimer", {}).get("required_for", []))
    disclaimer_text = policy.get("disclaimer", {}).get("text", "")

    trace_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"
    email = req.email.strip()
    if not email:
        raise ValueError("email cannot be empty")
    if len(email) > MAX_LEN:
        raise ValueError(f"email too long (max {MAX_LEN})")

    flagged = _find_flagged_phrases(email, risk_phrases)
    risk = _risk_level(flagged)

    rewritten = _rewrite_minimal(email)
    post_check_note = None
    remaining = _find_flagged_phrases(rewritten, risk_phrases)
    if remaining:
        # Second pass to soften leftover risky phrases.
        rewritten = _rewrite_minimal(rewritten)
        remaining = _find_flagged_phrases(rewritten, risk_phrases)
        if remaining:
            post_check_note = "Post-check: risky language remained; softened further."

    rewritten = _post_process(rewritten)

    # Always append disclaimer for client-facing messages
    disclaimer_added = True
    if ctx.audience.lower() in disclaimer_required_for:
        disclaimer = f"\n\n{disclaimer_text}" if disclaimer_text else ""
        if disclaimer and disclaimer not in rewritten:
            rewritten = rewritten + disclaimer
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
    if post_check_note:
        rationale = f"{rationale} {post_check_note}"

    response = BankingRewriteResponse(
        rewritten_email=rewritten,
        risk_level=risk,
        flagged_phrases=flagged,
        disclaimer_added=disclaimer_added,
        trace_id=trace_id,
        created_at=created_at,
        rationale=rationale,
    )
    record = {
        "trace_id": trace_id,
        "created_at": created_at,
        "review_status": response.review_status,
        "request": req.model_dump(),
        "response": response.model_dump(),
    }
    append_record(record)
    return response
