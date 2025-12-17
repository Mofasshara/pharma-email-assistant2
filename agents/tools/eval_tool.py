
def evaluate_output(text: str) -> bool:
    banned = ["guarantee", "100% safe"]
    return not any(word in text.lower() for word in banned)
