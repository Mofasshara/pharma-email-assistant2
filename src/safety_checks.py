def basic_safety_check(text: str) -> bool:
    forbidden_phrases = [
        "guaranteed cure",
        "100% safe",
        "no side effects"
    ]
    return not any(p.lower() in text.lower() for p in forbidden_phrases)
