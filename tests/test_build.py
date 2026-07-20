from recallrx.build import merge_records
from recallrx.models import ProductCode, RecallRecord


def make_record(record_id: str, source_url: str) -> RecallRecord:
    return RecallRecord(
        id=record_id,
        country="FR",
        authority="ANSM",
        local_id=record_id.removeprefix("FR_ANSM_"),
        date="2026-01-01",
        publication_date="2026-01-01",
        recall_class=None,
        product_type="medicine",
        medicine="Example medicine",
        manufacturer="Example laboratory",
        product_codes=[ProductCode(system="CIP", value="3400000000000")],
        lots=["LOT1"],
        source_url=source_url,
        confidence=0.9,
    )


def test_recall_record_json_round_trip():
    record = make_record("FR_ANSM_OLD", "https://example.test/recall")

    assert RecallRecord.from_json(record.to_json()) == record


def test_incremental_merge_replaces_changed_id_for_same_source():
    old = make_record("FR_ANSM_OLD", "https://example.test/recall")
    replacement = make_record("FR_ANSM_HASHED", "https://example.test/recall/")
    historical = make_record("FR_ANSM_HISTORY", "https://example.test/history")

    merged = merge_records([old, historical], [replacement])

    assert {record.id for record in merged} == {"FR_ANSM_HASHED", "FR_ANSM_HISTORY"}
