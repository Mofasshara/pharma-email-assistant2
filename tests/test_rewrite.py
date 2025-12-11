from src.services.rewrite_service import rewrite_email_llm


def test_basic_rewrite():
    text = "pls send info asap"
    result = rewrite_email_llm(text, "medical affairs")
    assert "rewritten_email" in result
