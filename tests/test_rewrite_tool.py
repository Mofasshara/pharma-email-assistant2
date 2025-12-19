from agents.tools.rewrite_tool import normalize_base_url


def test_normalize_adds_https():
    assert normalize_base_url("example.com") == "https://example.com"


def test_normalize_keeps_https():
    assert normalize_base_url("https://example.com/") == "https://example.com"


def test_normalize_empty():
    assert normalize_base_url("") == ""
