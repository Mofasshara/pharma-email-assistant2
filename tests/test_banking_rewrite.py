from src.banking.schemas import BankingRewriteRequest
from platform_layer.runtime.context import RuntimeContext
from src.banking.rewrite_service import rewrite_banking_email


def test_banking_rewrite_flags_and_disclaimer():
    req = BankingRewriteRequest(
        email=(
            "This product will give you excellent returns and is risk-free. "
            "You should buy."
        ),
        audience="client",
        language="en",
    )
    ctx = RuntimeContext(domain="banking", audience=req.audience, language=req.language)
    res = rewrite_banking_email(req, ctx)
    assert res.risk_level in {"medium", "high"}
    assert res.disclaimer_added is True
    assert len(res.flagged_phrases) >= 1
    assert "Disclaimer:" in res.rewritten_email
