from pathlib import Path

from recallrx.adapters.pt_infarmed import InfarmedPortugalAdapter, parse_portuguese_date


class DummyHttp:
    def get_text(self, url):
        return ""


def fixture(name):
    return Path("tests/fixtures").joinpath(name).read_text(encoding="utf-8")


def test_parse_portuguese_dates():
    assert parse_portuguese_date("03 jun 2026") == "2026-06-03"
    assert parse_portuguese_date("Data: 01/06/2026") == "2026-06-01"


def test_parse_infarmed_medicine_recall():
    adapter = InfarmedPortugalAdapter(http=DummyHttp())

    record = adapter.parse_html(
        fixture("infarmed_recall.html"),
        "https://www.infarmed.pt/web/infarmed/alertas/-/journal_content/56/15786/13121773",
    )

    assert record is not None
    assert record.id == "PT_INFARMED_CI_054_CD_550_20_001_2026"
    assert record.local_id == "CI 054/CD/550.20.001"
    assert record.date == "2026-06-03"
    assert record.publication_date == "2026-06-01"
    assert record.medicine == "Aciclovir Labesfal e Aciclovir Livixone 50 mg/g creme"
    assert record.manufacturer == "Generis Farmacêutica"
    assert [code.value for code in record.product_codes] == ["2621696", "5224688"]
    assert record.lots == ["E1743", "F1257", "E1744"]
    assert record.expiry_dates == ["Feb-28", "Sep-28"]


def test_rejects_infarmed_cosmetic_withdrawal():
    adapter = InfarmedPortugalAdapter(http=DummyHttp())

    record = adapter.parse_html(
        fixture("infarmed_cosmetic.html"),
        "https://www.infarmed.pt/web/infarmed/alertas/-/journal_content/56/15786/13152616",
    )

    assert record is None
