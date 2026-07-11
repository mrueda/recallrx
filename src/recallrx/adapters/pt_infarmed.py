from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from recallrx.adapters.base import Candidate
from recallrx.http import HttpClient
from recallrx.models import ProductCode, RecallRecord
from recallrx.text import clean_text, fold, unique


INFARMED_ALERTS_URL = "https://www.infarmed.pt/web/infarmed/alertas"
INFARMED_BASE_URL = "https://www.infarmed.pt"
PORTUGUESE_MONTHS = {
    "jan": "01",
    "janeiro": "01",
    "fev": "02",
    "fevereiro": "02",
    "mar": "03",
    "marco": "03",
    "março": "03",
    "abr": "04",
    "abril": "04",
    "mai": "05",
    "maio": "05",
    "jun": "06",
    "junho": "06",
    "jul": "07",
    "julho": "07",
    "ago": "08",
    "agosto": "08",
    "set": "09",
    "setembro": "09",
    "out": "10",
    "outubro": "10",
    "nov": "11",
    "novembro": "11",
    "dez": "12",
    "dezembro": "12",
}
PORTUGUESE_MONTH_PATTERN = "|".join(sorted(PORTUGUESE_MONTHS, key=len, reverse=True))


@dataclass
class InfarmedPortugalAdapter:
    http: HttpClient
    max_pages: int = 7
    request_delay_seconds: float = 0.25
    country: str = "PT"
    authority: str = "INFARMED"
    rejected: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def build(self) -> tuple[list[RecallRecord], dict]:
        candidates = self.discover()
        records: list[RecallRecord] = []
        seen_records: set[str] = set()

        for candidate in candidates:
            try:
                html = self.http.get_text(candidate.url)
                record = self.parse_html(html, candidate.url, candidate.title)
                if record is None:
                    self.rejected.append(
                        {"url": candidate.url, "title": candidate.title, "reason": "not_human_medicine_recall"}
                    )
                    continue
                if record.id in seen_records:
                    continue
                records.append(record)
                seen_records.add(record.id)
            except Exception as exc:  # pragma: no cover - exercised through integration runs
                self.rejected.append({"url": candidate.url, "title": candidate.title, "reason": str(exc)})

        records.sort(key=lambda item: (item.date, item.id), reverse=True)
        report = {
            "source": "pt_infarmed",
            "candidates": len(candidates),
            "accepted": len(records),
            "rejected": self.rejected,
            "warnings": self.warnings,
            "pages": self.max_pages,
        }
        return records, report

    def discover(self) -> list[Candidate]:
        candidates: list[Candidate] = []
        seen: set[str] = set()
        for page in range(1, self.max_pages + 1):
            html = self.http.get_text(self._page_url(page))
            soup = BeautifulSoup(html, "html.parser")
            page_candidates = 0
            for anchor in soup.find_all("a", href=True):
                title = clean_text(anchor.get_text(" "))
                href = str(anchor["href"])
                if "/web/infarmed/alertas/-/journal_content/" not in href:
                    continue
                if not self._title_could_be_recall(title):
                    continue
                url = urljoin(INFARMED_BASE_URL, href).split("#", 1)[0]
                if url in seen:
                    continue
                seen.add(url)
                candidates.append(
                    Candidate(
                        source_id=url.rsplit("/", 1)[-1],
                        title=self._candidate_title(title),
                        url=url,
                        excerpt=title,
                    )
                )
                page_candidates += 1
            if page > 1 and page_candidates == 0:
                break
            time.sleep(self.request_delay_seconds)
        return candidates

    def _page_url(self, page: int) -> str:
        if page <= 1:
            return INFARMED_ALERTS_URL
        params = {
            "p_p_id": "101_INSTANCE_Q8rB4MBkKBAb",
            "p_p_lifecycle": "0",
            "p_p_state": "normal",
            "p_p_mode": "view",
            "p_p_col_id": "column-1",
            "p_p_col_pos": "2",
            "p_p_col_count": "3",
            "_101_INSTANCE_Q8rB4MBkKBAb_delta": "10",
            "_101_INSTANCE_Q8rB4MBkKBAb_keywords": "",
            "_101_INSTANCE_Q8rB4MBkKBAb_advancedSearch": "false",
            "_101_INSTANCE_Q8rB4MBkKBAb_andOperator": "true",
            "p_r_p_564233524_resetCur": "false",
            "_101_INSTANCE_Q8rB4MBkKBAb_cur": str(page),
        }
        query = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{INFARMED_ALERTS_URL}?{query}"

    def _title_could_be_recall(self, title: str) -> bool:
        text = fold(title)
        return "recolha" in text or "retirada do mercado" in text

    def _candidate_title(self, title: str) -> str:
        title = re.sub(r"\s+Circular Informativa\s+N\.?\s*[ºo]?.*$", "", title, flags=re.IGNORECASE)
        return clean_text(title)

    def parse_html(self, html: str, source_url: str, fallback_title: str | None = None) -> RecallRecord | None:
        soup = BeautifulSoup(html, "html.parser")
        article = soup.select_one(".article-content") or soup
        title = self._page_title(soup) or fallback_title or ""
        article_text = clean_text(article.get_text("\n", strip=True))
        article_text_with_breaks = article.get_text("\n", strip=True)

        alert_type = self._extract_alert_type(article_text_with_breaks)
        if alert_type and alert_type != "med":
            return None
        if not self._title_could_be_recall(title):
            return None

        circular = self._extract_circular(article_text)
        publication_date = self._extract_circular_date(article_text)
        date = self._extract_article_date(article_text_with_breaks) or publication_date
        if not circular or not date:
            return None

        local_id = self._local_id(circular, date)
        product_codes = [ProductCode(system="AIM", value=value) for value in self._extract_registration_numbers(article)]
        lots = self._extract_lots(article)
        expiry_dates = self._extract_expiry_dates(article)
        medicine = self._extract_medicine(title)
        manufacturer = self._extract_manufacturer(article_text)
        reason = self._extract_reason(article)
        actions = self._extract_actions(article_text)
        warnings = []
        if not product_codes:
            warnings.append("missing_registration_number")
        if not lots:
            warnings.append("missing_lot")
        if not manufacturer:
            warnings.append("missing_manufacturer")

        return RecallRecord(
            id=f"PT_INFARMED_{local_id}",
            country=self.country,
            authority=self.authority,
            local_id=circular,
            date=date,
            publication_date=publication_date,
            recall_class=None,
            product_type="medicine",
            medicine=medicine or title,
            manufacturer=manufacturer,
            product_codes=product_codes,
            lots=lots,
            expiry_dates=expiry_dates,
            reason=reason,
            actions=actions,
            source_url=source_url,
            pdf_url=None,
            confidence=0.9 if product_codes and lots else 0.78,
            warnings=warnings,
            raw={
                "title": title,
                "alert_type": alert_type,
                "source": "pt_infarmed",
            },
        )

    def _page_title(self, soup: BeautifulSoup) -> str:
        meta = soup.find("meta", property="og:title")
        if meta and meta.get("content"):
            return clean_text(str(meta["content"]))
        heading = soup.find(["h1", "h2"])
        return clean_text(heading.get_text(" ") if heading else "")

    def _extract_alert_type(self, text: str) -> str | None:
        match = re.search(r"Tipo de alerta:\s*([A-Za-z]+)", text, flags=re.IGNORECASE)
        return fold(match.group(1)) if match else None

    def _extract_circular(self, text: str) -> str | None:
        match = re.search(
            r"Circular Informativa\s+N\.?\s*[ºo]?\s*([0-9]{3}/[A-Z]+/[0-9.]+)",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            return None
        return f"CI {match.group(1).upper()}"

    def _extract_circular_date(self, text: str) -> str | None:
        match = re.search(
            r"Circular Informativa\s+N\.?\s*[ºo]?\s*[0-9]{3}/[A-Z]+/[0-9.]+(?:\s+de|\s+Data:)\s+(\d{1,2}/\d{1,2}/\d{4})",
            text,
            flags=re.IGNORECASE,
        )
        return parse_portuguese_date(match.group(1)) if match else None

    def _extract_article_date(self, text: str) -> str | None:
        for line in text.splitlines():
            if re.search(rf"\b(?:{PORTUGUESE_MONTH_PATTERN})\.?\b", fold(line)):
                parsed = parse_portuguese_date(line)
                if parsed:
                    return parsed
        return None

    def _local_id(self, circular: str, date: str) -> str:
        value = circular.replace("CI ", "")
        value = re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")
        return f"CI_{value}_{date[:4]}"

    def _extract_medicine(self, title: str) -> str:
        value = title
        patterns = [
            r"^Recolha voluntária de lotes dos medicamentos?\s+",
            r"^Recolha voluntária de lotes do medicamento\s+",
            r"^Recolha voluntária de medicamentos?\s*\|\s*",
            r"^Recolha voluntária de lotes?\s*\|\s*",
            r"^Recolha voluntária do medicamento\s+",
            r"^Recolha voluntária de lote:\s*",
            r"^Recolha voluntária lote\s*\|\s*",
            r"^Recolha de lotes dos medicamentos?\s+",
            r"^Recolha de lote do medicamento\s+",
            r"^Recolha do medicamento\s+",
        ]
        for pattern in patterns:
            value = re.sub(pattern, "", value, flags=re.IGNORECASE)
        return clean_text(value.strip(" |:-"))

    def _extract_manufacturer(self, text: str) -> str | None:
        patterns = [
            r"\bA empresa\s+([^.\n]+?)(?:\s+irá|\s+vai|\s+procedeu|,)",
            r"\btitular de autorização de introdução no mercado\s+([^.\n]+)",
            r"\btitular de AIM\s+([^.\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return clean_text(match.group(1).strip(" ,"))
        return None

    def _extract_registration_numbers(self, article: BeautifulSoup) -> list[str]:
        values: list[str] = []
        for table in article.find_all("table"):
            rows = self._table_rows(table)
            if not rows:
                continue
            headers = [fold(cell) for cell in rows[0]]
            reg_indexes = [index for index, header in enumerate(headers) if "registo" in header]
            for row in rows[1:]:
                for index in reg_indexes:
                    if index < len(row) and re.fullmatch(r"\d{6,8}", row[index]):
                        values.append(row[index])

        text = article.get_text(" ", strip=True)
        for match in re.finditer(r"(?:n[.ºo]\s*(?:de\s+)?|número de\s+)registo\s+(\d{6,8})", text, flags=re.IGNORECASE):
            values.append(match.group(1))
        return unique(values)

    def _extract_lots(self, article: BeautifulSoup) -> list[str]:
        values: list[str] = []
        for table in article.find_all("table"):
            rows = self._table_rows(table)
            if not rows:
                continue
            headers = [fold(cell) for cell in rows[0]]
            lot_indexes = [index for index, header in enumerate(headers) if "lote" in header]
            for row in rows[1:]:
                if lot_indexes:
                    for index in lot_indexes:
                        if index < len(row):
                            values.append(row[index])
                    if len(row) == 2 and all(index >= 2 for index in lot_indexes):
                        values.append(row[0])

        text = article.get_text(" ", strip=True)
        values.extend(re.findall(r"\bn[.ºo]\s*([A-Z0-9]{5,14})\s*\(validade", text, flags=re.IGNORECASE))
        values.extend(re.findall(r"\blotes?\s+n[.ºo]\s*([A-Z0-9]{5,14})", text, flags=re.IGNORECASE))
        product_codes = set(self._extract_registration_numbers(article))
        return unique([value for value in values if self._looks_like_lot(value) and value not in product_codes])

    def _extract_expiry_dates(self, article: BeautifulSoup) -> list[str]:
        values: list[str] = []
        for table in article.find_all("table"):
            rows = self._table_rows(table)
            if not rows:
                continue
            headers = [fold(cell) for cell in rows[0]]
            expiry_indexes = [
                index for index, header in enumerate(headers) if "validade" in header or "valid" in header
            ]
            for row in rows[1:]:
                for index in expiry_indexes:
                    if index < len(row):
                        values.append(row[index])
                if len(row) == 2 and all(index >= 3 for index in expiry_indexes):
                    values.append(row[1])

        text = article.get_text(" ", strip=True)
        values.extend(re.findall(r"validade:?\s*(\d{1,2}/\d{1,2}/\d{4})", text, flags=re.IGNORECASE))
        return unique(values)

    def _table_rows(self, table) -> list[list[str]]:
        rows: list[list[str]] = []
        for tr in table.find_all("tr"):
            cells = [clean_text(cell.get_text(" ")) for cell in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        return rows

    def _looks_like_lot(self, value: str) -> bool:
        value = clean_text(value)
        if not value or len(value) < 3:
            return False
        if re.search(r"[/-]", value):
            return False
        if not re.search(r"\d", value):
            return False
        return bool(re.fullmatch(r"[A-Za-z0-9]+", value))

    def _extract_reason(self, article: BeautifulSoup) -> str | None:
        for paragraph in article.find_all("p"):
            text = clean_text(paragraph.get_text(" "))
            folded = fold(text)
            if len(text) > 80 and ("detetad" in folded or "sequencia" in folded or "por ter" in folded):
                return text
        return None

    def _extract_actions(self, text: str) -> str | None:
        match = re.search(r"(Face ao exposto[:\s].+)$", text, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(1))[:800]
        match = re.search(r"(Assim, o Infarmed determina.+?)(?:Face ao exposto|$)", text, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(1))[:800]
        return None


def parse_portuguese_date(value: str | None) -> str | None:
    text = clean_text(value)
    if not text:
        return None

    numeric = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b", text)
    if numeric:
        day, month, year = numeric.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"

    words = re.search(
        r"\b(\d{1,2})\s+([A-Za-zÁÉÍÓÚÀÂÊÔÃÕÇáéíóúàâêôãõç]{3,})\.?\s+(\d{4})\b",
        text,
        flags=re.IGNORECASE,
    )
    if words:
        day, month_name, year = words.groups()
        month = PORTUGUESE_MONTHS.get(fold(month_name))
        if month:
            return f"{year}-{month}-{int(day):02d}"

    return None
