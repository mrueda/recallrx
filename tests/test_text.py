from openrecall.text import parse_spanish_date


def test_parse_spanish_word_date():
    assert parse_spanish_date("3 de junio de 2026") == "2026-06-03"


def test_parse_numeric_date():
    assert parse_spanish_date("25.05.2026") == "2026-05-25"
