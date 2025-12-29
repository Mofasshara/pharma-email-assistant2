from agents import orchestrator


def test_handle_request_defaults_to_pharma(monkeypatch):
    def fake_route_request(_text: str) -> str:
        return "PHARMA"

    def fake_rewrite_email(text: str, audience: str, request_id: str | None = None):
        return {"rewritten_email": f"{text}::{audience}::{request_id}"}

    monkeypatch.setattr(orchestrator, "route_request", fake_route_request)
    monkeypatch.setattr(orchestrator, "rewrite_email", fake_rewrite_email)

    result = orchestrator.handle_request(
        "hello",
        "client",
        domain="pharma",
        request_id="req-123",
    )

    assert result["rewritten_email"] == "hello::client::req-123"
