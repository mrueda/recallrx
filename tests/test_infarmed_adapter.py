from pathlib import Path

from bs4 import BeautifulSoup

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


def test_historical_discovery_keeps_content_pages_and_canonicalizes_urls():
    listing = """
    <div class="result-item">
      <h3 class="title"><a href="https://www.infarmed.pt/web/infarmed/alertas-de-seguranca?p_p_id=101&amp;_101_assetEntryId=12345&amp;_101_type=content&amp;_101_urlTitle=recolha-medicamento">Recolha de lote | Medicamento</a></h3>
      <div class="result-resume"><p>A empresa Example Pharma irá recolher o medicamento com número de registo 7654321, lote n.º LOT123, validade 12/2027.</p></div>
      <div class="result-path"><span>17/07/2026</span></div>
    </div>
    <div class="result-item">
      <h3 class="title"><a href="https://www.infarmed.pt/web/infarmed/alertas-de-seguranca?p_p_id=101&amp;_101_assetEntryId=12346&amp;_101_type=document">Circular Informativa</a></h3>
      <div class="result-path"><span>17/07/2026</span></div>
    </div>
    <div class="result-item">
      <h3 class="title"><a href="https://www.infarmed.pt/web/infarmed/alertas-de-seguranca?p_p_id=101&amp;_101_assetEntryId=12347&amp;_101_type=content&amp;_101_urlTitle=recolha-antiga">Recolha de lote | Antigo</a></h3>
      <div class="result-path"><span>17/07/2019</span></div>
    </div>
    """

    class SearchHttp:
        def get_text(self, url):
            return listing

    adapter = InfarmedPortugalAdapter(
        http=SearchHttp(), mode="full", start_year=2020, max_history_pages=1, request_delay_seconds=0
    )

    candidates = adapter.discover()

    assert len(candidates) == 1
    assert candidates[0].source_id == "12345"
    assert "_101_assetEntryId=12345" in candidates[0].url
    assert "_101_type=content" in candidates[0].url
    assert "redirect=" not in candidates[0].url

    fallback = adapter._record_from_history_result(candidates[0])
    assert fallback is not None
    assert fallback.id == "PT_INFARMED_ASSET_12345"
    assert [code.value for code in fallback.product_codes] == ["7654321"]
    assert fallback.lots == ["LOT123"]
    assert "source_detail_fallback" in fallback.warnings


def test_extracts_plain_text_infarmed_registration_lot_and_expiry():
    article = BeautifulSoup(
        "<div>Medicamento (n.º de registo 8575902) MA04JLF 30-04-2028</div>", "html.parser"
    )
    adapter = InfarmedPortugalAdapter(http=DummyHttp())

    assert adapter._extract_registration_numbers(article) == ["8575902"]
    assert adapter._extract_lots(article) == ["MA04JLF"]
    assert adapter._extract_expiry_dates(article) == ["30-04-2028"]
