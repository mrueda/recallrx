from pathlib import Path

from openrecall_es.adapters.es_aemps import AempsSpainAdapter


class DummyHttp:
    def get_bytes(self, url):
        return b""


def fixture(name):
    return Path("tests/fixtures").joinpath(name).read_text(encoding="utf-8")


def test_parse_human_medicine_recall():
    adapter = AempsSpainAdapter(http=DummyHttp())

    record = adapter.parse_html(
        fixture("aemps_recall.html"),
        "https://www.aemps.gob.es/informa/oculotect-50-mg-ml-colirio-en-solucion/",
    )

    assert record is not None
    assert record.id == "ES_AEMPS_R_21_2026"
    assert record.local_id == "R_21/2026"
    assert record.date == "2026-06-03"
    assert record.publication_date == "2026-06-04"
    assert record.product_codes[0].system == "CN"
    assert record.product_codes[0].value == "755215"
    assert record.lots == ["ABC123", "ABC124"]
    assert record.recall_class == "2"
    assert record.pdf_url.endswith("R21_2026.pdf")


def test_rejects_veterinary_alerts():
    adapter = AempsSpainAdapter(http=DummyHttp())

    record = adapter.parse_html(
        fixture("aemps_veterinary.html"),
        "https://www.aemps.gob.es/informa/nicilan/",
    )

    assert record is None


def test_discovery_queries_include_broad_recall_terms():
    adapter = AempsSpainAdapter(http=DummyHttp())

    queries = adapter.discovery_queries()

    assert "Retirada medicamento lote" in queries
    assert "defecto calidad medicamento" in queries
    assert any(query.startswith("Nº alerta medicamento ") for query in queries)
