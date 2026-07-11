from pathlib import Path

from recallrx.adapters.fr_ansm import AnsmFranceAdapter, parse_french_date


class DummyHttp:
    def get_text(self, url):
        return ""


def fixture(name):
    return Path("tests/fixtures").joinpath(name).read_text(encoding="utf-8")


def test_parse_french_date():
    assert parse_french_date("10/07/2026") == "2026-07-10"


def test_parse_ansm_medicine_recall():
    adapter = AnsmFranceAdapter(http=DummyHttp())

    record = adapter.parse_html(
        fixture("ansm_recall.html"),
        "https://ansm.sante.fr/informations-de-securite/chloraprep-solution-pour-application-cutanee",
    )

    assert record is not None
    assert record.country == "FR"
    assert record.date == "2026-07-10"
    assert record.local_id.startswith("SLUG_CHLORAPREP")
    assert record.medicine == "Chloraprep, solution pour application cutanée 60 ampoules en verre de 1 ml avec applicateur"
    assert record.manufacturer == "Becton Dickinson France"
    assert [code.value for code in record.product_codes] == ["3400955062400"]
    assert record.lots == ["5175366", "5200357"]
    assert record.expiry_dates == ["30/06/2028", "31/07/2028"]
    assert "perte de stérilité" in record.reason


def test_rejects_ansm_device_recall():
    adapter = AnsmFranceAdapter(http=DummyHttp())

    record = adapter.parse_html(
        fixture("ansm_device.html"),
        "https://ansm.sante.fr/informations-de-securite/rapid-refill-continuous-injection-system",
    )

    assert record is None
