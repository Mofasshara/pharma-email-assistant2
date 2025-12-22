from src.banking import audit_store
from src.banking.api import banking_review_action
from src.banking.schemas import BankingRewriteRequest, ReviewActionRequest
from src.banking.rewrite_service import rewrite_banking_email


def _configure_audit_paths(tmp_path, monkeypatch):
    audit_dir = tmp_path / "audit"
    audit_file = audit_dir / "banking_rewrites.jsonl"
    review_events_file = audit_dir / "banking_review_events.jsonl"
    monkeypatch.setattr(audit_store, "AUDIT_DIR", audit_dir)
    monkeypatch.setattr(audit_store, "AUDIT_FILE", audit_file)
    monkeypatch.setattr(audit_store, "REVIEW_EVENTS_FILE", review_events_file)
    return audit_file, review_events_file


def _create_record():
    req = BankingRewriteRequest(
        email="This product will give you excellent returns and is risk-free.",
        audience="client",
        language="en",
    )
    return rewrite_banking_email(req)


def test_audit_write_and_read(tmp_path, monkeypatch):
    audit_file, _ = _configure_audit_paths(tmp_path, monkeypatch)
    response = _create_record()

    assert audit_file.exists()
    assert len(audit_file.read_text(encoding="utf-8").strip().splitlines()) == 1

    record = audit_store.get_record(response.trace_id)
    assert record is not None
    assert record["trace_id"] == response.trace_id


def test_review_action_approve_sets_status(tmp_path, monkeypatch):
    _configure_audit_paths(tmp_path, monkeypatch)
    response = _create_record()

    payload = ReviewActionRequest(action="approve", reviewer="qa", comment="ok")
    banking_review_action(response.trace_id, payload)

    record = audit_store.get_record(response.trace_id)
    assert record["review_status"] == "approve"
    assert record["response"]["review_status"] == "approve"


def test_review_action_edit_changes_output(tmp_path, monkeypatch):
    _configure_audit_paths(tmp_path, monkeypatch)
    response = _create_record()
    edited = "Edited compliant version of the email."

    payload = ReviewActionRequest(
        action="edit",
        reviewer="qa",
        comment="softened",
        edited_email=edited,
    )
    banking_review_action(response.trace_id, payload)

    record = audit_store.get_record(response.trace_id)
    assert record["review_status"] == "edit"
    assert record["response"]["rewritten_email"] == edited


def test_review_action_reject_preserves_output(tmp_path, monkeypatch):
    _configure_audit_paths(tmp_path, monkeypatch)
    response = _create_record()
    original = response.rewritten_email

    payload = ReviewActionRequest(action="reject", reviewer="qa", comment="too strong")
    banking_review_action(response.trace_id, payload)

    record = audit_store.get_record(response.trace_id)
    assert record["review_status"] == "reject"
    assert record["response"]["rewritten_email"] == original
