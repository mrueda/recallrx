from __future__ import annotations

import html
import re
import unicodedata

SPANISH_MONTHS = {
    "enero": "01",
    "febrero": "02",
    "marzo": "03",
    "abril": "04",
    "mayo": "05",
    "junio": "06",
    "julio": "07",
    "agosto": "08",
    "septiembre": "09",
    "setiembre": "09",
    "octubre": "10",
    "noviembre": "11",
    "diciembre": "12",
}


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value).strip()


def fold(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower()


def parse_spanish_date(value: str | None) -> str | None:
    text = clean_text(value)
    if not text:
        return None

    numeric = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b", text)
    if numeric:
        day, month, year = numeric.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    words = re.search(
        r"\b(\d{1,2})\s+de\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)\s+de\s+(\d{4})\b",
        text,
        flags=re.IGNORECASE,
    )
    if words:
        day, month_name, year = words.groups()
        month = SPANISH_MONTHS.get(fold(month_name))
        if month:
            return f"{year}-{month}-{int(day):02d}"

    return None


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = clean_text(value)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result
