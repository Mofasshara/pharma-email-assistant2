def _extract_text(output: object) -> str:
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        candidate = output.get("rewritten_email") or output.get("response")
        if isinstance(candidate, str):
            return candidate
    return str(output)


def evaluate_output(output: object) -> bool:
    banned = ["guarantee", "100% safe"]
    text = _extract_text(output)
    return not any(word in text.lower() for word in banned)
