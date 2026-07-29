import json
from pathlib import Path

from recallrx.report import render_build_summary


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_render_build_summary_reports_current_sources_by_country(tmp_path):
    write_json(
        tmp_path / "metadata.json",
        {
            "collection_mode": "incremental",
            "generated_at": "2026-07-29T04:20:00+00:00",
            "record_count": 261,
            "sources_updated": ["es_aemps", "pt_infarmed"],
            "countries": [
                {"code": "es", "iso2": "ES", "records": 157},
                {"code": "pt", "iso2": "PT", "records": 104},
            ],
        },
    )
    write_json(
        tmp_path / "countries" / "es" / "build-report.json",
        {
            "reports": [
                {
                    "source": "es_aemps",
                    "candidates": 21,
                    "accepted": 21,
                    "rejected": [],
                    "warnings": ["duplicate_id"],
                    "stored_before": 156,
                }
            ]
        },
    )
    write_json(
        tmp_path / "countries" / "pt" / "build-report.json",
        {
            "reports": [
                {
                    "source": "pt_infarmed",
                    "candidates": 36,
                    "accepted": 25,
                    "rejected": [{"reason": "not_human_medicine_recall"}] * 11,
                    "warnings": [],
                    "fallback_records": 2,
                    "stored_before": 104,
                },
                {
                    "source": "old_source",
                    "candidates": 999,
                    "accepted": 999,
                    "stored_before": 0,
                },
            ]
        },
    )

    summary = render_build_summary(tmp_path)

    assert "| ES | `es_aemps` | 21 | 21 | 0 | 1 | 157 | +1 |" in summary
    assert "| PT | `pt_infarmed` | 36 | 25 | 11 | 2 | 104 | +0 |" in summary
    assert "| **Run total** |  | **57** | **46** | **11** | **3** | **261** | **+1** |" in summary
    assert "old_source" not in summary


def test_render_build_summary_handles_no_reports(tmp_path):
    write_json(
        tmp_path / "metadata.json",
        {
            "collection_mode": "full",
            "generated_at": "2026-07-29T04:20:00+00:00",
            "record_count": 0,
            "countries": [],
        },
    )

    assert "_No source reports were generated._" in render_build_summary(tmp_path)
