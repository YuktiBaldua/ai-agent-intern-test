from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentChunk:
    filename: str
    document_id: str
    title: str
    status: str
    effective_date: str
    audience: str
    policy_authority: str
    heading: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def customer_eligible(self) -> bool:
        return (
            self.status == "active"
            and self.audience == "customer"
            and self.policy_authority == "official"
        )

    @property
    def source_label(self) -> str:
        return f"{self.filename} — {self.heading}"
