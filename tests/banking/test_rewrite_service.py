from src.banking.rewrite_service import DISCLAIMER, rewrite_banking_email
from src.banking.schemas import BankingRewriteRequest


def test_risk_level_low_when_no_phrases():
    req = BankingRewriteRequest(
        email="Hello team, here is the update for this quarter.",
        audience="client",
        language="en",
    )
    res = rewrite_banking_email(req)
    assert res.risk_level == "low"
    assert res.flagged_phrases == []


def test_risk_level_medium_with_one_phrase():
    req = BankingRewriteRequest(
        email="This product offers guaranteed returns.",
        audience="client",
        language="en",
    )
    res = rewrite_banking_email(req)
    assert res.risk_level == "medium"
    assert res.flagged_phrases == ["guaranteed returns"]


def test_risk_level_medium_with_two_phrases():
    req = BankingRewriteRequest(
        email="This is risk-free and you should buy now.",
        audience="client",
        language="en",
    )
    res = rewrite_banking_email(req)
    assert res.risk_level == "medium"
    assert res.flagged_phrases == ["risk-free", "you should buy"]


def test_risk_level_high_with_three_phrases():
    req = BankingRewriteRequest(
        email="Guaranteed returns, no risk, and you should buy today.",
        audience="client",
        language="en",
    )
    res = rewrite_banking_email(req)
    assert res.risk_level == "high"
    assert res.flagged_phrases == ["guaranteed returns", "no risk", "you should buy"]


def test_disclaimer_added_for_client():
    req = BankingRewriteRequest(
        email="This product will give you excellent returns.",
        audience="client",
        language="en",
    )
    res = rewrite_banking_email(req)
    assert res.disclaimer_added is True
    assert DISCLAIMER in res.rewritten_email


def test_disclaimer_not_added_for_internal():
    req = BankingRewriteRequest(
        email="This product will give you excellent returns.",
        audience="internal",
        language="en",
    )
    res = rewrite_banking_email(req)
    assert res.disclaimer_added is False
    assert DISCLAIMER not in res.rewritten_email


def test_post_check_removes_risky_terms():
    req = BankingRewriteRequest(
        email="This is guaranteed returns and you should buy now.",
        audience="client",
        language="en",
    )
    res = rewrite_banking_email(req)
    lowered = res.rewritten_email.lower()
    assert "guaranteed" not in lowered
    assert "you should buy" not in lowered
