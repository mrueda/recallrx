from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from recallrx.adapters.registry import DEFAULT_SOURCES, create_adapter
from recallrx.http import HttpClient
from recallrx.models import RecallRecord


DEFAULT_CONFIG_PATH = Path("recallrx.config.json")
CollectionMode = Literal["incremental", "full"]


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


def build_dataset(
    output: Path,
    sources: list[str] | None = None,
    config_path: Path | None = None,
    mode: CollectionMode = "incremental",
) -> dict[str, Any]:
    if mode not in {"incremental", "full"}:
        raise ValueError(f"Unsupported collection mode: {mode}")

    output.mkdir(parents=True, exist_ok=True)
    config = load_config(config_path)
    selected_sources = sources or enabled_sources(config)
    http = HttpClient()
    reports_by_country: dict[str, list[dict[str, Any]]] = {}
    collected_by_country: dict[str, list[RecallRecord]] = {}
    selected_countries: set[str] = set()

    for source in selected_sources:
        adapter = create_adapter(source, http=http, config=config, mode=mode)
        records, report = adapter.build()
        country = adapter.country.lower()
        selected_countries.add(country)
        report = {**report, "country": country, "mode": mode}
        reports_by_country.setdefault(country, []).append(report)
        collected_by_country.setdefault(country, []).extend(records)

    countries = []
    configured_countries = list(config.get("countries", {}))
    stored_countries_root = output / "countries"
    stored_countries = (
        sorted(path.name for path in stored_countries_root.iterdir() if path.is_dir())
        if stored_countries_root.exists()
        else []
    )
    all_country_codes = configured_countries + [
        country
        for country in sorted(set(stored_countries) | set(collected_by_country))
        if country not in configured_countries
    ]
    for country in all_country_codes:
        existing = load_country_records(output, country)
        collected = deduplicate_records(collected_by_country.get(country, []))
        if country not in selected_countries:
            records = existing
        elif mode == "incremental":
            records = merge_records(existing, collected)
        else:
            records = collected

        info = country_info(config, country)
        country_root = output / "countries" / country
        if country in selected_countries or not country_root.exists():
            reports = reports_by_country.get(country, [])
            for report in reports:
                report["stored_before"] = len(existing)
                report["stored_after"] = len(records)
            write_country(output, country, records, reports, info)
        countries.append({**info, "records": len(records)})

    metadata = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "collection_mode": mode,
        "countries": countries,
        "default_country": config.get("default_country", countries[0]["code"] if countries else None),
        "sources": enabled_sources(config),
        "sources_updated": selected_sources,
        "record_count": sum(item["records"] for item in countries),
    }
    write_json(output / "metadata.json", metadata)
    return metadata


def load_country_records(output: Path, country: str) -> list[RecallRecord]:
    recalls_root = output / "countries" / country / "recalls"
    if not recalls_root.exists():
        return []
    return [
        RecallRecord.from_json(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(recalls_root.glob("*.json"))
    ]


def deduplicate_records(records: list[RecallRecord]) -> list[RecallRecord]:
    return list({record.id: record for record in records}.values())


def merge_records(existing: list[RecallRecord], collected: list[RecallRecord]) -> list[RecallRecord]:
    merged = {record.id: record for record in existing}
    ids_by_source = {
        record.source_url.rstrip("/"): record.id
        for record in existing
        if record.source_url
    }
    for record in collected:
        source_key = record.source_url.rstrip("/")
        previous_id = ids_by_source.get(source_key)
        if previous_id and previous_id != record.id:
            merged.pop(previous_id, None)
        merged[record.id] = record
        if source_key:
            ids_by_source[source_key] = record.id
    return list(merged.values())


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
