from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_build_summary(root: Path) -> str:
    metadata = read_json(root / "metadata.json")
    updated_sources = set(metadata.get("sources_updated", []))
    rows: list[dict[str, Any]] = []

    for country in metadata.get("countries", []):
        code = str(country.get("code", "")).lower()
        report_path = root / "countries" / code / "build-report.json"
        if not code or not report_path.exists():
            continue

        reports = read_json(report_path).get("reports", [])
        if updated_sources:
            reports = [report for report in reports if report.get("source") in updated_sources]
        if not reports:
            continue

        stored_before = max((as_int(report.get("stored_before")) for report in reports), default=0)
        retained = as_int(country.get("records"))
        rows.append(
            {
                "country": str(country.get("iso2") or code.upper()),
                "sources": ", ".join(sorted({str(report.get("source", "unknown")) for report in reports})),
                "collected": sum(as_int(report.get("candidates")) for report in reports),
                "accepted": sum(as_int(report.get("accepted")) for report in reports),
                "rejected": sum(item_count(report.get("rejected")) for report in reports),
                "warnings": sum(
                    item_count(report.get("warnings")) + as_int(report.get("fallback_records"))
                    for report in reports
                ),
                "retained": retained,
                "net": retained - stored_before,
            }
        )

    lines = [
        "## RecallRx collection summary",
        "",
        f"- Mode: `{escape_markdown(metadata.get('collection_mode', 'unknown'))}`",
        f"- Generated: `{escape_markdown(metadata.get('generated_at', 'unknown'))}`",
        f"- Dataset records: **{as_int(metadata.get('record_count'))}**",
        "",
    ]
    if not rows:
        lines.append("_No source reports were generated._")
        return "\n".join(lines)

    lines.extend(
        [
            "| Country | Source | Collected | Accepted | Rejected | Warnings | Retained | Net |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| {country} | `{sources}` | {collected} | {accepted} | {rejected} | {warnings} | {retained} | {net} |".format(
                country=escape_markdown(row["country"]),
                sources=escape_markdown(row["sources"]),
                collected=row["collected"],
                accepted=row["accepted"],
                rejected=row["rejected"],
                warnings=row["warnings"],
                retained=row["retained"],
                net=format_change(row["net"]),
            )
        )

    lines.append(
        "| **Run total** |  | **{collected}** | **{accepted}** | **{rejected}** | **{warnings}** | **{retained}** | **{net}** |".format(
            collected=sum(row["collected"] for row in rows),
            accepted=sum(row["accepted"] for row in rows),
            rejected=sum(row["rejected"] for row in rows),
            warnings=sum(row["warnings"] for row in rows),
            retained=sum(row["retained"] for row in rows),
            net=format_change(sum(row["net"] for row in rows)),
        )
    )
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def item_count(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    return as_int(value)


def format_change(value: int) -> str:
    return f"{value:+d}"


def escape_markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
