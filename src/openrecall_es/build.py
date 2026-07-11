from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openrecall_es.adapters.registry import DEFAULT_SOURCES, create_adapter
from openrecall_es.http import HttpClient
from openrecall_es.models import RecallRecord


DEFAULT_CONFIG_PATH = Path("openrecall.config.json")


def load_config(path: Path | None = None) -> dict[str, Any]:
    config_path = path or DEFAULT_CONFIG_PATH
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {
        "default_country": "es",
        "countries": {},
        "sources": [{"name": source, "country": source.split("_", 1)[0], "enabled": True} for source in DEFAULT_SOURCES],
    }


def enabled_sources(config: dict[str, Any]) -> list[str]:
    sources = config.get("sources", [])
    selected = [source["name"] for source in sources if source.get("enabled", True)]
    return selected or DEFAULT_SOURCES


def country_info(config: dict[str, Any], country: str) -> dict[str, Any]:
    info = dict(config.get("countries", {}).get(country, {}))
    info.setdefault("code", country)
    info.setdefault("iso2", country.upper())
    info.setdefault("name", country.upper())
    info.setdefault("authority", "")
    info.setdefault("flag", "")
    return info


def build_dataset(output: Path, sources: list[str] | None = None, config_path: Path | None = None) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    config = load_config(config_path)
    selected_sources = sources or enabled_sources(config)
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
        info = country_info(config, country)
        write_country(output, country, records, all_reports, info)
        countries.append({**info, "records": len(records)})

    metadata = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "countries": countries,
        "default_country": config.get("default_country", countries[0]["code"] if countries else None),
        "sources": selected_sources,
        "record_count": sum(item["records"] for item in countries),
    }
    write_json(output / "metadata.json", metadata)
    return metadata


def write_country(
    output: Path,
    country: str,
    records: list[RecallRecord],
    reports: list[dict[str, Any]],
    info: dict[str, Any] | None = None,
) -> None:
    info = info or {"code": country, "iso2": country.upper(), "name": country.upper(), "authority": "", "flag": ""}
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
            **info,
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
