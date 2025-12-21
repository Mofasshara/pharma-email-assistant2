import json
import uuid
from typing import Any
from pathlib import Path

from src.services.rewrite_service import rewrite_email_llm

PROMPT_PATH = Path("shared/prompts/banking/risk_rewrite_v1.txt")

RISK_PHRASES = {
    "HIGH": [
        "guaranteed",
        "will outperform",
        "risk-free",
        "certain returns",
        "best investment",
    ],
    "MEDIUM": ["you should buy", "recommend", "strong buy", "safe profit"],
}
DISCLAIMER = (
    "This message is for informational purposes only and does not constitute "
    "investment advice."
)


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def detect_risk(text: str) -> tuple[str, list[str]]:
    t = text.lower()
    flags = []
    level = "LOW"
    for phrase in RISK_PHRASES["HIGH"]:
        if phrase in t:
            flags.append(phrase)
            level = "HIGH"
    if level != "HIGH":
        for phrase in RISK_PHRASES["MEDIUM"]:
            if phrase in t:
                flags.append(phrase)
                level = "MEDIUM"
    return level, flags

def _parse_model_output(raw: Any) -> dict:
    if isinstance(raw, dict) and "error" in raw and "raw" in raw:
        candidate = raw["raw"].strip()
        if candidate.startswith("```"):
            lines = candidate.splitlines()
            candidate = "\n".join(lines[1:-1]).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


def banking_risk_rewrite(text: str, audience: str) -> dict:
    trace_id = str(uuid.uuid4())
    prompt = load_prompt()
    risk_level, flags = detect_risk(text)

    raw = rewrite_email_llm(text, audience, prompt_override=prompt)

    data = _parse_model_output(raw)
    if "rewritten_email" in data and "rewritten_text" not in data:
        data["rewritten_text"] = data["rewritten_email"]
    if isinstance(data.get("explanation"), list):
        data["explanation"] = " ".join(data["explanation"])
    data.setdefault("risk_level", risk_level)
    data.setdefault("flags", flags)
    data.setdefault("disclaimer_added", False)
    data.setdefault("explanation", "Auto-generated fallback.")
    if risk_level in ["MEDIUM", "HIGH"]:
        if "disclaimer_added" not in data:
            data["disclaimer_added"] = True
        rewritten = data.get("rewritten_text", "")
        if DISCLAIMER.lower() not in rewritten.lower():
            data["rewritten_text"] = rewritten.rstrip() + "\n\n" + DISCLAIMER
            data["disclaimer_added"] = True

    data["trace_id"] = trace_id
    return data
