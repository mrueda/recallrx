from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openrecall_es.adapters.registry import DEFAULT_SOURCES, create_adapter
from openrecall_es.http import HttpClient
from openrecall_es.models import RecallRecord


def build_dataset(output: Path, sources: list[str] | None = None) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    selected_sources = sources or DEFAULT_SOURCES
    http = HttpClient()
    all_reports: list[dict[str, Any]] = []
    records_by_country: dict[str, list[RecallRecord]] = {}

    for source in selected_sources:
        adapter = create_adapter(source, http=http)
        records, report = adapter.build()
        all_reports.append(report)
        records_by_country.setdefault(adapter.country.lower(), []).extend(records)

    countries = []
    for country, records in sorted(records_by_country.items()):
        write_country(output, country, records, all_reports)
        countries.append({"code": country, "records": len(records)})

    metadata = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "countries": countries,
        "sources": selected_sources,
        "record_count": sum(item["records"] for item in countries),
    }
    write_json(output / "metadata.json", metadata)
    return metadata


def write_country(output: Path, country: str, records: list[RecallRecord], reports: list[dict[str, Any]]) -> None:
    base = output / "countries" / country
    if base.exists():
        shutil.rmtree(base)
    (base / "recalls").mkdir(parents=True, exist_ok=True)
    (base / "by-code").mkdir(parents=True, exist_ok=True)
    (base / "by-year").mkdir(parents=True, exist_ok=True)

    records = sorted(records, key=lambda item: (item.date, item.id), reverse=True)
    for record in records:
        write_json(base / "recalls" / f"{record.id}.json", record.to_json())

    write_json(base / "recalls-summary.json", [record.to_summary() for record in records])
    write_json(
        base / "metadata.json",
        {
            "country": country.upper(),
            "record_count": len(records),
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
    )
    write_indexes(base, records)
    write_json(base / "build-report.json", {"reports": reports})


def write_indexes(base: Path, records: list[RecallRecord]) -> None:
    by_code: dict[str, list[str]] = {}
    by_year: dict[str, list[str]] = {}
    for record in records:
        year = record.date[:4]
        by_year.setdefault(year, []).append(record.id)
        for code in record.product_codes:
            key = f"{code.system.lower()}-{code.value}"
            by_code.setdefault(key, []).append(record.id)

    for key, values in sorted(by_code.items()):
        write_json(base / "by-code" / f"{key}.json", sorted(values))
    for year, values in sorted(by_year.items()):
        write_json(base / "by-year" / f"{year}.json", sorted(values))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
