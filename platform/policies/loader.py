from pathlib import Path

import yaml

POLICY_DIR = Path("platform/policies")


def load_policy(domain: str) -> dict:
    path = POLICY_DIR / f"{domain}_policy.yaml"
    if not path.exists():
        raise FileNotFoundError(f"No policy for domain={domain}")
    return yaml.safe_load(path.read_text())
