from pathlib import Path

from recallrx.adapters.es_aemps import AempsSpainAdapter


class DummyHttp:
    def get_json(self, url, params=None):
        return []

    def get_text(self, url):
        return ""

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


def test_wp_post_discovery_finds_human_medicine_recalls():
    class PostHttp(DummyHttp):
        def get_json(self, url, params=None):
            if params["page"] == 1:
                return [
                    {
                        "id": 1,
                        "date": "2026-06-04T08:35:50",
                        "link": "https://www.aemps.gob.es/informa/oculotect/",
                        "title": {"rendered": "OCULOTECT"},
                        "excerpt": {"rendered": "<p>Nº alerta: R_21/2026 Producto: Medicamento</p>"},
                        "content": {"rendered": "<p>Medicamento de uso humano</p>"},
                    },
                    {
                        "id": 2,
                        "date": "2026-06-03T08:35:50",
                        "link": "https://www.aemps.gob.es/informa/veterinario/",
                        "title": {"rendered": "Veterinario"},
                        "excerpt": {"rendered": "<p>Nº alerta: R_01/2026 Producto: Medicamento veterinario</p>"},
                        "content": {"rendered": ""},
                    },
                ]
            return []

    adapter = AempsSpainAdapter(http=PostHttp(), request_delay_seconds=0)

    candidates = adapter.discover()

    assert [candidate.url for candidate in candidates] == ["https://www.aemps.gob.es/informa/oculotect/"]
