from dataclasses import dataclass


@dataclass
class RuntimeContext:
    domain: str
    audience: str
    language: str = "en"
    tenant_id: str | None = None
