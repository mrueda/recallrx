from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from recallrx.adapters.base import Candidate
from recallrx.http import HttpClient
from recallrx.models import ProductCode, RecallRecord
from recallrx.text import clean_text, fold, unique


ANSM_SECURITY_URL = "https://ansm.sante.fr/informations-de-securite/"
ANSM_BASE_URL = "https://ansm.sante.fr"


@dataclass
class AnsmFranceAdapter:
    http: HttpClient
    max_pages: int = 20
    request_delay_seconds: float = 0.2
    country: str = "FR"
    authority: str = "ANSM"
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
                        {"url": candidate.url, "title": candidate.title, "reason": "not_medicine_product_recall"}
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
            "source": "fr_ansm",
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
            for anchor in soup.find_all("a", href=True):
                text = clean_text(anchor.get_text(" "))
                href = str(anchor["href"])
                if "/informations-de-securite/" not in href:
                    continue
                if not self._listing_text_is_medicine_recall(text):
                    continue
                url = urljoin(ANSM_BASE_URL, href).split("#", 1)[0]
                if url in seen:
                    continue
                seen.add(url)
                candidates.append(
                    Candidate(
                        source_id=url.rstrip("/").rsplit("/", 1)[-1],
                        title=self._candidate_title(text),
                        url=url,
                        excerpt=text,
                    )
                )
            time.sleep(self.request_delay_seconds)
        return candidates

    def _page_url(self, page: int) -> str:
        if page <= 1:
            return ANSM_SECURITY_URL
        return f"{ANSM_SECURITY_URL}?page={page}"

    def _listing_text_is_medicine_recall(self, text: str) -> bool:
        normalized = fold(text)
        return "rappel de produit" in normalized and "medicaments" in normalized

    def _candidate_title(self, text: str) -> str:
        value = re.sub(r"^RAPPEL DE PRODUIT\s+Médicaments\s+PUBLIÉ LE\s+\d{2}/\d{2}/\d{4}\s+", "", text)
        value = re.sub(r"\s+Rappel n[°o].*$", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\s+Niveau de rappel\s*:.*$", "", value, flags=re.IGNORECASE)
        return clean_text(value)

    def parse_html(self, html: str, source_url: str, fallback_title: str | None = None) -> RecallRecord | None:
        soup = BeautifulSoup(html, "html.parser")
        page_text = clean_text(soup.get_text("\n", strip=True))
        header_match = re.search(
            r"RAPPEL DE PRODUIT\s*-\s*Médicaments\s*-\s*PUBLIÉ LE\s*(\d{2}/\d{2}/\d{4})",
            page_text,
            flags=re.IGNORECASE,
        )
        if not header_match:
            return None

        title = self._page_title(soup) or fallback_title or ""
        date = parse_french_date(header_match.group(1))
        local_id = self._extract_local_id(page_text, source_url)
        product_codes = [ProductCode(system="CIP", value=value) for value in self._extract_cip_codes(page_text)]
        lots = self._extract_lots(page_text)
        expiry_dates = self._extract_expiry_dates(page_text)
        medicine, manufacturer = self._split_title(title)
        reason = self._extract_reason(page_text)
        actions = self._extract_actions(page_text)
        warnings = []
        if not product_codes:
            warnings.append("missing_cip")
        if not lots:
            warnings.append("missing_lot")
        if not manufacturer:
            warnings.append("missing_manufacturer")

        return RecallRecord(
            id=f"FR_ANSM_{local_id}",
            country=self.country,
            authority=self.authority,
            local_id=local_id,
            date=date,
            publication_date=date,
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
            raw={"title": title, "source": "fr_ansm"},
        )

    def _page_title(self, soup: BeautifulSoup) -> str:
        heading = soup.find("h1")
        return clean_text(heading.get_text(" ") if heading else "")

    def _extract_local_id(self, text: str, source_url: str) -> str:
        match = re.search(r"\bRappel n[°o]\s*(R\d{6,})\b", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()
        slug = source_url.rstrip("/").rsplit("/", 1)[-1]
        return f"SLUG_{slug_token(slug, 80)}"

    def _extract_cip_codes(self, text: str) -> list[str]:
        values = []
        for match in re.finditer(r"\bCIP\s+([0-9][0-9\s]{6,20})\b", text, flags=re.IGNORECASE):
            digits = re.sub(r"\D", "", match.group(1))
            if len(digits) in {7, 13}:
                values.append(digits)
        return unique(values)

    def _extract_lots(self, text: str) -> list[str]:
        values = re.findall(r"\bLot\s+([A-Z0-9][A-Z0-9.-]{2,24})", text, flags=re.IGNORECASE)
        return unique([value.strip(".") for value in values])

    def _extract_expiry_dates(self, text: str) -> list[str]:
        values = re.findall(r"\bpéremption le\s+(\d{2}/\d{2}/\d{4})", text, flags=re.IGNORECASE)
        return unique(values)

    def _split_title(self, title: str) -> tuple[str, str | None]:
        parts = [clean_text(part) for part in re.split(r"\s+[–—]\s+", title) if clean_text(part)]
        if len(parts) >= 2:
            return " – ".join(parts[:-1]), parts[-1]
        return title, None

    def _extract_reason(self, text: str) -> str | None:
        sentences = re.split(r"(?<=[.])\s+", text)
        for sentence in sentences:
            folded = fold(sentence)
            if "fait suite" in folded or "risque" in folded or "defaut" in folded:
                return clean_text(sentence)[:800]
        return None

    def _extract_actions(self, text: str) -> str | None:
        match = re.search(r"(Niveau de rappel\s*:.+?)(?:Le laboratoire|$)", text, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(1))[:800]
        match = re.search(r"(Ce rappel .+?)(?:Si vous avez|$)", text, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(1))[:800]
        return None


def parse_french_date(value: str | None) -> str:
    text = clean_text(value)
    match = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b", text)
    if not match:
        raise ValueError(f"Unsupported French date: {value!r}")
    day, month, year = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def slug_token(value: str, max_length: int) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    token = re.sub(r"[^A-Za-z0-9]+", "_", ascii_value.upper()).strip("_")
    return token[:max_length].strip("_") or "UNKNOWN"
