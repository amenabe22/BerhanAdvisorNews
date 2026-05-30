from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ExtractedContent:
    title: str
    content: str
    published_at: datetime | None = None
    author: str | None = None
    language: str = "en"
    attachments: list[dict[str, str]] = field(default_factory=list)
    directive_number: str | None = None
    directive_type_code: str | None = None
    raw_html: str = ""
    canonical_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "author": self.author,
            "language": self.language,
            "attachments": self.attachments,
            "directive_number": self.directive_number,
            "directive_type_code": self.directive_type_code,
            "raw_html": self.raw_html,
            "canonical_url": self.canonical_url,
        }
