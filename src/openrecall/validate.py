from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_RECORD_FIELDS = {
    "id",
    "country",
    "authority",
    "local_id",
    "date",
    "medicine",
    "product_codes",
    "lots",
    "source_url",
    "confidence",
}


def validate_dataset(root: Path) -> list[str]:
    errors: list[str] = []
    metadata_path = root / "metadata.json"
    if not metadata_path.exists():
        return ["missing data/metadata.json"]
    metadata = read_json(metadata_path)
    if "countries" not in metadata:
        errors.append("metadata.json missing countries")

    for country in metadata.get("countries", []):
        code = country.get("code")
        if not code:
            errors.append("country entry missing code")
            continue
        country_root = root / "countries" / code
        summary_path = country_root / "recalls-summary.json"
        if not summary_path.exists():
            errors.append(f"{code}: missing recalls-summary.json")
            continue
        summaries = read_json(summary_path)
        if not isinstance(summaries, list):
            errors.append(f"{code}: recalls-summary.json is not a list")
            continue
        ids = set()
        for summary in summaries:
            errors.extend(validate_record(summary, f"{code}:summary"))
            record_id = summary.get("id")
            if record_id in ids:
                errors.append(f"{code}: duplicate id {record_id}")
            ids.add(record_id)
            detail = country_root / "recalls" / f"{record_id}.json"
            if not detail.exists():
                errors.append(f"{code}: missing detail for {record_id}")
            else:
                errors.extend(validate_record(read_json(detail), f"{code}:{record_id}"))

    for pdf in root.rglob("*.pdf"):
        errors.append(f"PDF should not be committed: {pdf}")
    return errors


def validate_record(record: dict[str, Any], context: str) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_RECORD_FIELDS - set(record)
    if missing:
        errors.append(f"{context}: missing fields {sorted(missing)}")
    if not str(record.get("id", "")).startswith(f"{record.get('country', '')}_{record.get('authority', '')}_"):
        errors.append(f"{context}: id is not country/authority scoped")
    if not record.get("source_url", "").startswith("https://"):
        errors.append(f"{context}: source_url must be https")
    if not isinstance(record.get("product_codes", []), list):
        errors.append(f"{context}: product_codes must be a list")
    if not isinstance(record.get("lots", []), list):
        errors.append(f"{context}: lots must be a list")
    return errors


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
