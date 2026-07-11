from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from recallrx.models import RecallRecord


@dataclass(frozen=True)
class Candidate:
    source_id: str
    title: str
    url: str
    excerpt: str = ""


class SourceAdapter(Protocol):
    country: str
    authority: str

    def build(self) -> tuple[list[RecallRecord], dict]:
        """Return normalized recall records and source-specific build report."""
