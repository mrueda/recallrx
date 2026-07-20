from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup

from recallrx.adapters.base import Candidate
from recallrx.http import HttpClient
from recallrx.models import ProductCode, RecallRecord
from recallrx.text import clean_text, fold, unique


INFARMED_ALERTS_URL = "https://www.infarmed.pt/web/infarmed/alertas"
INFARMED_SEARCH_URL = "https://www.infarmed.pt/web/infarmed/alertas-de-seguranca"
INFARMED_BASE_URL = "https://www.infarmed.pt"
INFARMED_HUMAN_MEDICINE_CATEGORY = "20616"
HISTORY_QUERIES = ("recolha", '"retirada do mercado"')
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
    max_history_pages: int = 10
    history_page_size: int = 200
    request_delay_seconds: float = 0.25
    start_year: int = 2020
    mode: str = "incremental"
    country: str = "PT"
    authority: str = "INFARMED"
    rejected: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    pages_fetched: int = 0
    semantic_retries: int = 0
    history_fallbacks: dict[str, dict[str, str]] = field(default_factory=dict)
    fallback_records: int = 0

    def build(self) -> tuple[list[RecallRecord], dict]:
        candidates = self.discover()
        records: list[RecallRecord] = []
        seen_records: dict[str, str] = {}

        for candidate in candidates:
            try:
                html = self.http.get_text(candidate.url)
                record = self.parse_html(html, candidate.url, candidate.title)
                if record is None and self.mode == "full":
                    self.semantic_retries += 1
                    time.sleep(self.request_delay_seconds)
                    html = self.http.get_text(candidate.url)
                    record = self.parse_html(html, candidate.url, candidate.title)
                if record is None and self.mode == "full":
                    record = self._record_from_history_result(candidate)
                    if record is not None:
                        self.fallback_records += 1
                if record is None:
                    self.rejected.append(
                        {"url": candidate.url, "title": candidate.title, "reason": "not_human_medicine_recall"}
                    )
                    continue
                if record.id in seen_records:
                    self.warnings.append(
                        f"duplicate_record_id id={record.id} urls={seen_records[record.id]},{candidate.url}"
                    )
                    continue
                records.append(record)
                seen_records[record.id] = candidate.url
            except Exception as exc:  # pragma: no cover - exercised through integration runs
                self.rejected.append({"url": candidate.url, "title": candidate.title, "reason": str(exc)})

        records.sort(key=lambda item: (item.date, item.id), reverse=True)
        report = {
            "source": "pt_infarmed",
            "candidates": len(candidates),
            "accepted": len(records),
            "rejected": self.rejected,
            "warnings": self.warnings,
            "mode": self.mode,
            "discovery": "historical_search" if self.mode == "full" else "recent_alerts",
            "pages": self.pages_fetched,
            "semantic_retries": self.semantic_retries,
            "fallback_records": self.fallback_records,
        }
        return records, report

    def discover(self) -> list[Candidate]:
        if self.mode == "full":
            return self._discover_history()
        return self._discover_recent()

    def _discover_recent(self) -> list[Candidate]:
        candidates: list[Candidate] = []
        seen: set[str] = set()
        for page in range(1, self.max_pages + 1):
            html = self.http.get_text(self._recent_page_url(page))
            self.pages_fetched += 1
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

    def _discover_history(self) -> list[Candidate]:
        candidates: list[Candidate] = []
        seen: set[str] = set()
        for query in HISTORY_QUERIES:
            for page in range(1, self.max_history_pages + 1):
                html = self.http.get_text(self._history_page_url(query, page))
                self.pages_fetched += 1
                soup = BeautifulSoup(html, "html.parser")
                items = soup.select(".result-item")
                if not items:
                    break

                page_dates: list[str] = []
                for item in items:
                    anchor = item.select_one("h3.title a[href]")
                    if anchor is None:
                        continue
                    title = clean_text(anchor.get_text(" "))
                    params = parse_qs(urlparse(str(anchor["href"])).query)
                    if params.get("_101_type") != ["content"]:
                        continue

                    result_date = self._history_result_date(item)
                    if result_date:
                        page_dates.append(result_date)
                        if int(result_date[:4]) < self.start_year:
                            continue
                    if not self._title_could_be_recall(title):
                        continue

                    asset_id = self._first_query_value(params, "_101_assetEntryId")
                    if not asset_id or asset_id in seen:
                        continue
                    seen.add(asset_id)
                    self.history_fallbacks[asset_id] = {
                        "html": str(item),
                        "date": result_date or "",
                    }
                    candidates.append(
                        Candidate(
                            source_id=asset_id,
                            title=self._candidate_title(title),
                            url=self._canonical_content_url(params),
                            excerpt=result_date or title,
                        )
                    )

                if page_dates and max(page_dates)[:4] < str(self.start_year):
                    break
                if len(items) < self.history_page_size:
                    break
                time.sleep(self.request_delay_seconds)
        return candidates

    def _recent_page_url(self, page: int) -> str:
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

    def _history_page_url(self, query: str, page: int) -> str:
        params = {
            "p_p_id": "3",
            "p_p_lifecycle": "0",
            "p_p_state": "maximized",
            "p_p_mode": "view",
            "_3_struts_action": "/search/search",
            "_3_keywords": query,
            "_3_delta": str(self.history_page_size),
            "_3_groupId": "15786",
            "_3_assetCategoryIds": INFARMED_HUMAN_MEDICINE_CATEGORY,
            "_3_paginationPhase": "true",
            "_3_reorderBy": "orderByDate",
            "_3_resetCur": "false",
            "_3_cur": str(page),
        }
        return f"{INFARMED_SEARCH_URL}?{urlencode(params)}"

    def _history_result_date(self, item) -> str | None:
        for node in reversed(item.select(".result-path")):
            parsed = parse_portuguese_date(node.get_text(" "))
            if parsed:
                return parsed
        return None

    def _canonical_content_url(self, params: dict[str, list[str]]) -> str:
        stable_params = {
            "p_p_id": "101",
            "p_p_lifecycle": "0",
            "p_p_state": "maximized",
            "p_p_mode": "view",
            "_101_struts_action": "/asset_publisher/view_content",
            "_101_assetEntryId": self._first_query_value(params, "_101_assetEntryId"),
            "_101_type": "content",
            "_101_urlTitle": self._first_query_value(params, "_101_urlTitle"),
            "inheritRedirect": "false",
        }
        filtered_params = {key: value for key, value in stable_params.items() if value}
        return f"{INFARMED_SEARCH_URL}?{urlencode(filtered_params)}"

    def _first_query_value(self, params: dict[str, list[str]], name: str) -> str:
        values = params.get(name, [])
        return values[0] if values else ""

    def _record_from_history_result(self, candidate: Candidate) -> RecallRecord | None:
        fallback = self.history_fallbacks.get(candidate.source_id)
        if not fallback or not fallback.get("date"):
            return None

        article = BeautifulSoup(fallback["html"], "html.parser")
        text = clean_text(article.get_text(" ", strip=True))
        date = fallback["date"]
        product_codes = [
            ProductCode(system="AIM", value=value) for value in self._extract_registration_numbers(article)
        ]
        lots = self._extract_lots(article)
        expiry_dates = self._extract_expiry_dates(article)
        manufacturer = self._extract_manufacturer(text)
        warnings = ["source_detail_fallback"]
        if not product_codes:
            warnings.append("missing_registration_number")
        if not lots:
            warnings.append("missing_lot")
        if not manufacturer:
            warnings.append("missing_manufacturer")

        local_id = f"ASSET_{candidate.source_id}"
        return RecallRecord(
            id=f"PT_INFARMED_{local_id}",
            country=self.country,
            authority=self.authority,
            local_id=local_id,
            date=date,
            publication_date=date,
            recall_class=None,
            product_type="medicine",
            medicine=self._extract_medicine(candidate.title) or candidate.title,
            manufacturer=manufacturer,
            product_codes=product_codes,
            lots=lots,
            expiry_dates=expiry_dates,
            reason=self._extract_reason(article),
            actions=self._extract_actions(text),
            source_url=candidate.url,
            pdf_url=None,
            confidence=0.72 if product_codes and lots else 0.6,
            warnings=warnings,
            raw={
                "title": candidate.title,
                "source": "pt_infarmed_search_result",
                "asset_id": candidate.source_id,
            },
        )

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
            title = clean_text(str(meta["content"]))
            return re.sub(r"\s+-\s+Alertas de segurança$", "", title, flags=re.IGNORECASE)
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
            r"\bA empresa\s+(.+?)(?:,\s+|\s+)(?:irá|vai|procedeu)\b",
            r"\btitular de autorização de introdução no mercado\s+([^.\n]+)",
            r"\btitular de AIM\s+([^.\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                value = clean_text(match.group(1).strip(" ,"))
                return re.sub(r",?\s+S\.?\s*A\.?$", "", value, flags=re.IGNORECASE)
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
        for match in re.finditer(
            r"(?:n[.]?\s*[ºo]?\s*(?:de\s+)?|número de\s+)registo\s+(\d{6,8})",
            text,
            flags=re.IGNORECASE,
        ):
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
        number_marker = r"n[.]?\s*[ºo]?"
        values.extend(
            re.findall(
                rf"\b{number_marker}\s*([A-Z0-9]{{5,14}})\s*(?:\(\s*)?(?:com\s+a\s+)?validade",
                text,
                flags=re.IGNORECASE,
            )
        )
        values.extend(
            re.findall(rf"\blotes?\s+{number_marker}\s*([A-Z0-9]{{5,14}})", text, flags=re.IGNORECASE)
        )
        values.extend(
            match.group(1)
            for match in re.finditer(r"\b([A-Z0-9]{5,14})\s+\d{2}[-/]\d{2}[-/]\d{4}\b", text)
            if self._looks_like_lot(match.group(1))
        )
        values.extend(
            match.group(1)
            for match in re.finditer(r"\b([A-Z0-9]{4,14})\s+\d{2}/\d{4}\b", text)
            if self._looks_like_lot(match.group(1))
        )
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
        values.extend(re.findall(r"\b[A-Z0-9]{5,14}\s+(\d{2}[-/]\d{2}[-/]\d{4})\b", text))
        values.extend(re.findall(r"\b[A-Z0-9]{4,14}\s+(\d{2}/\d{4})\b", text))
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
