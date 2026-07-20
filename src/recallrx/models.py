from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProductCode:
    system: str
    value: str

    def to_json(self) -> dict[str, str]:
        return {"system": self.system, "value": self.value}


@dataclass
class RecallRecord:
    id: str
    country: str
    authority: str
    local_id: str
    date: str
    publication_date: str | None
    recall_class: str | None
    product_type: str | None
    medicine: str
    manufacturer: str | None
    product_codes: list[ProductCode] = field(default_factory=list)
    lots: list[str] = field(default_factory=list)
    expiry_dates: list[str] = field(default_factory=list)
    reason: str | None = None
    actions: str | None = None
    source_url: str = ""
    pdf_url: str | None = None
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "RecallRecord":
        return cls(
            id=payload["id"],
            country=payload["country"],
            authority=payload["authority"],
            local_id=payload["local_id"],
            date=payload["date"],
            publication_date=payload.get("publication_date"),
            recall_class=payload.get("recall_class"),
            product_type=payload.get("product_type"),
            medicine=payload["medicine"],
            manufacturer=payload.get("manufacturer"),
            product_codes=[ProductCode(**code) for code in payload.get("product_codes", [])],
            lots=list(payload.get("lots", [])),
            expiry_dates=list(payload.get("expiry_dates", [])),
            reason=payload.get("reason"),
            actions=payload.get("actions"),
            source_url=payload.get("source_url", ""),
            pdf_url=payload.get("pdf_url"),
            confidence=float(payload.get("confidence", 0.0)),
            warnings=list(payload.get("warnings", [])),
            raw=dict(payload.get("raw", {})),
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "country": self.country,
            "authority": self.authority,
            "local_id": self.local_id,
            "date": self.date,
            "publication_date": self.publication_date,
            "recall_class": self.recall_class,
            "product_type": self.product_type,
            "medicine": self.medicine,
            "manufacturer": self.manufacturer,
            "product_codes": [code.to_json() for code in self.product_codes],
            "lots": self.lots,
            "expiry_dates": self.expiry_dates,
            "reason": self.reason,
            "actions": self.actions,
            "source_url": self.source_url,
            "pdf_url": self.pdf_url,
            "confidence": self.confidence,
            "warnings": self.warnings,
            "raw": self.raw,
        }

    def to_summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "country": self.country,
            "authority": self.authority,
            "local_id": self.local_id,
            "date": self.date,
            "publication_date": self.publication_date,
            "recall_class": self.recall_class,
            "medicine": self.medicine,
            "manufacturer": self.manufacturer,
            "product_codes": [code.to_json() for code in self.product_codes],
            "lots": self.lots,
            "reason": self.reason,
            "source_url": self.source_url,
            "pdf_url": self.pdf_url,
            "confidence": self.confidence,
            "warnings": self.warnings,
        }
