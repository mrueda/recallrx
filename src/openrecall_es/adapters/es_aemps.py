from __future__ import annotations

import re
import time
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from openrecall_es.adapters.base import Candidate
from openrecall_es.http import HttpClient
from openrecall_es.models import ProductCode, RecallRecord
from openrecall_es.text import clean_text, fold, parse_spanish_date, unique


AEMPS_SEARCH_URL = "https://www.aemps.gob.es/wp-json/aemps-search/v1/search"
AEMPS_POSTS_URL = "https://www.aemps.gob.es/wp-json/wp/v2/posts"
AEMPS_BASE_URL = "https://www.aemps.gob.es"
BASE_DISCOVERY_QUERIES = [
    "Nº alerta",
    "Formato pdf Nº alerta",
    "Marca comercial Lote",
    "Producto Medicamento Lote",
    "Retirada medicamento lote",
    "Retirada del mercado medicamento",
    "defecto calidad medicamento",
    "Marca comercial presentación código nacional",
    "Medidas cautelares adoptadas",
]


@dataclass
class AempsSpainAdapter:
    http: HttpClient
    max_pages: int = 60
    posts_per_page: int = 100
    request_delay_seconds: float = 0.35
    start_year: int = 2020
    country: str = "ES"
    authority: str = "AEMPS"
    rejected: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def build(self) -> tuple[list[RecallRecord], dict]:
        candidates = self.discover()
        records: list[RecallRecord] = []
        seen_records: set[str] = set()

        for candidate in candidates:
            try:
                html = self.http.get_text(candidate.url)
                record = self.parse_html(html, candidate.url)
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
            "source": "es_aemps",
            "candidates": len(candidates),
            "accepted": len(records),
            "rejected": self.rejected,
            "warnings": self.warnings,
            "discovery_queries": self.discovery_queries(),
        }
        return records, report

    def discovery_queries(self) -> list[str]:
        queries = list(BASE_DISCOVERY_QUERIES)
        for year in self.discovery_years():
            queries.extend(
                [
                    f"Nº alerta medicamento {year}",
                    f"retirada medicamento lote {year}",
                    f"defecto calidad medicamento {year}",
                ]
            )
        return unique(queries)

    def discovery_years(self) -> list[int]:
        current_year = datetime.now().year
        return list(range(current_year, self.start_year - 1, -1))

    def discover(self) -> list[Candidate]:
        candidates = self._discover_wp_posts()
        if candidates:
            return candidates
        return self._discover_search_endpoint()

    def _discover_wp_posts(self) -> list[Candidate]:
        seen: set[str] = set()
        candidates: list[Candidate] = []
        for page in range(1, self.max_pages + 1):
            try:
                payload = self.http.get_json(
                    AEMPS_POSTS_URL,
                    params={
                        "per_page": self.posts_per_page,
                        "page": page,
                        "orderby": "date",
                        "order": "desc",
                        "_fields": "id,date,link,title,excerpt,content",
                    },
                )
            except requests.exceptions.RetryError as exc:
                self.warnings.append(f"wp_posts_rate_limited page={page}: {exc}")
                break
            except requests.exceptions.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else "unknown"
                self.warnings.append(f"wp_posts_http_error status={status} page={page}: {exc}")
                break
            if not isinstance(payload, list) or not payload:
                break

            stop = False
            for item in payload:
                post_year = self._post_year(item)
                if post_year is not None and post_year < self.start_year:
                    stop = True
                    continue
                if not self._post_could_be_recall(item):
                    continue
                url = clean_text(item.get("link", ""))
                if not url or url in seen:
                    continue
                seen.add(url)
                candidates.append(
                    Candidate(
                        source_id=str(item.get("id", "")),
                        title=self._rendered_text(item.get("title", {})),
                        url=url,
                        excerpt=self._rendered_text(item.get("excerpt", {})),
                    )
                )
            if stop:
                break
            time.sleep(self.request_delay_seconds)
        return candidates

    def _discover_search_endpoint(self) -> list[Candidate]:
        seen: set[str] = set()
        candidates: list[Candidate] = []
        for query in self.discovery_queries():
            page = 1
            while page <= self.max_pages:
                try:
                    payload = self.http.get_json(
                        AEMPS_SEARCH_URL,
                        params={"post_type": "post", "search": query, "page": page},
                    )
                except requests.exceptions.RetryError as exc:
                    self.warnings.append(f"discovery_rate_limited query={query!r} page={page}: {exc}")
                    break
                except requests.exceptions.HTTPError as exc:
                    status = exc.response.status_code if exc.response is not None else "unknown"
                    self.warnings.append(f"discovery_http_error status={status} query={query!r} page={page}: {exc}")
                    break
                if not isinstance(payload, list) or not payload:
                    break
                for item in payload:
                    if not self._candidate_could_be_recall(item):
                        continue
                    url = clean_text(item.get("url", ""))
                    if not url or url in seen:
                        continue
                    seen.add(url)
                    candidates.append(
                        Candidate(
                            source_id=str(item.get("id", "")),
                            title=clean_text(item.get("title", "")),
                            url=url,
                            excerpt=clean_text(item.get("excerpt", "")),
                        )
                    )
                if len(payload) < 10:
                    break
                page += 1
                time.sleep(self.request_delay_seconds)
        return candidates

    def _post_year(self, item: dict) -> int | None:
        date = str(item.get("date", ""))
        if not re.match(r"^\d{4}", date):
            return None
        return int(date[:4])

    def _post_could_be_recall(self, item: dict) -> bool:
        html = " ".join(
            [
                self._rendered_html(item.get("title", {})),
                self._rendered_html(item.get("excerpt", {})),
                self._rendered_html(item.get("content", {})),
                str(item.get("link", "")),
            ]
        )
        ids = re.findall(r"\bR_\d+/\d{4}\b", html)
        if not any(int(local_id[-4:]) >= self.start_year for local_id in ids):
            return False

        text = fold(BeautifulSoup(html, "html.parser").get_text(" "))
        positive = "medicamento" in text or "formula magistral" in text or "medicamentosusohumano" in text
        negative = (
            "veterinario" in text
            or "cosmetico" in text
            or "cosmeticos" in text
            or "producto sanitario" in text
            or "productos sanitarios" in text
        )
        return positive and not negative

    def _rendered_html(self, value: object) -> str:
        if isinstance(value, dict):
            return str(value.get("rendered", ""))
        return str(value or "")

    def _rendered_text(self, value: object) -> str:
        html = self._rendered_html(value)
        if "<" not in html and ">" not in html:
            return clean_text(html)
        return clean_text(BeautifulSoup(html, "html.parser").get_text(" "))

    def _candidate_could_be_recall(self, item: dict) -> bool:
        text = fold(" ".join([str(item.get("title", "")), str(item.get("excerpt", "")), str(item.get("url", ""))]))
        positive = (
            "n alerta" in text
            or "formato pdf" in text
            or "retirada" in text
            or "defecto de calidad" in text
            or "medicamentosusohumano" in text
        )
        negative = (
            "vdc" in text
            or "veterinario" in text
            or "cosmetico" in text
            or "cosmeticos" in text
            or "productos sanitarios" in text
            or "producto sanitario" in text
        )
        return positive and not negative

    def parse_html(self, html: str, source_url: str) -> RecallRecord | None:
        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article") or soup
        title = clean_text(article.find("h1").get_text(" ") if article.find("h1") else "")
        full_text = clean_text(article.get_text(" "))

        local_id = self._extract_local_id(full_text)
        if not local_id:
            return None
        if not re.fullmatch(r"R_\d+/\d{4}", local_id):
            return None

        labels = self._extract_labels(article)
        product_type = self._first_label(labels, "producto", "productos")
        if product_type and "medicamento" not in fold(product_type) and "formula magistral" not in fold(product_type):
            return None

        publication_date = parse_spanish_date(self._extract_after(full_text, "Fecha de publicación:"))
        recall_date = parse_spanish_date(self._first_label(labels, "fecha")) or parse_spanish_date(full_text)
        medicine = (
            self._first_label(
                labels,
                "marca comercial y presentacion",
                "marca comercial, presentacion, numero de registro y codigo nacional",
                "marca comercial",
                "productos",
            )
            or title
        )
        cn_values = unique(re.findall(r"\bCN[:\s]*([0-9]{5,8})\b", f"{title} {full_text}", flags=re.IGNORECASE))
        lots = self._extract_lots(labels, full_text)
        expiry_dates = self._split_values(
            self._first_label(labels, "fecha de caducidad", "fechas de caducidad") or ""
        )
        manufacturer = self._first_label(
            labels,
            "laboratorio titular",
            "titular de la autorizacion de comercializacion",
            "titular de autorizacion de comercializacion",
            "laboratorio fabricante",
            "laboratorio responsable",
            "fabricante",
        )
        recall_class = self._extract_recall_class(labels, full_text)
        reason = self._first_label(labels, "descripcion del defecto", "motivo", "defecto detectado")
        actions = self._first_label(labels, "medidas cautelares adoptadas", "medidas", "actuaciones")
        pdf_url = self._extract_pdf_url(soup, source_url)

        warnings: list[str] = []
        if not recall_date:
            warnings.append("missing_recall_date")
        if not cn_values:
            warnings.append("missing_cn")
        if not lots:
            warnings.append("missing_lots")
        if not reason:
            warnings.append("missing_reason")
        if not manufacturer:
            warnings.append("missing_manufacturer")

        if pdf_url and self._needs_pdf_fallback(warnings):
            self._apply_pdf_fallback(pdf_url, warnings)

        confidence = self._confidence(warnings)
        canonical_id = self._canonical_id(local_id)
        return RecallRecord(
            id=f"ES_AEMPS_{canonical_id}",
            country=self.country,
            authority=self.authority,
            local_id=local_id,
            date=recall_date or publication_date or "1970-01-01",
            publication_date=publication_date,
            recall_class=recall_class,
            product_type=product_type,
            medicine=medicine,
            manufacturer=manufacturer,
            product_codes=[ProductCode(system="CN", value=value) for value in cn_values],
            lots=lots,
            expiry_dates=expiry_dates,
            reason=reason,
            actions=actions,
            source_url=source_url,
            pdf_url=pdf_url,
            confidence=confidence,
            warnings=warnings,
            raw={"title": title, "parser": "aemps_html"},
        )

    def _extract_labels(self, article) -> dict[str, str]:
        labels: dict[str, str] = {}
        for row in article.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if not cells:
                continue
            row_text = [clean_text(cell.get_text(" ")) for cell in cells]
            combined = " ".join(row_text)
            inline = self._label_value_from_text(combined)
            labels.update(inline)

            strong = row.find("strong")
            if strong:
                label = self._normalize_label(strong.get_text(" "))
                value_parts: list[str] = []
                for cell in cells:
                    text = clean_text(cell.get_text(" "))
                    strong_text = clean_text(strong.get_text(" "))
                    value_parts.append(clean_text(text.replace(strong_text, "", 1).strip(" :")))
                value = clean_text(" ".join(value_parts))
                if label and value:
                    labels.setdefault(label, value)
        return labels

    def _label_value_from_text(self, text: str) -> dict[str, str]:
        labels: dict[str, str] = {}
        for match in re.finditer(
            r"([A-ZÁÉÍÓÚÜÑa-záéíóúüñº/ ,]+?):\s*([^:]+?)(?=\s+[A-ZÁÉÍÓÚÜÑa-záéíóúüñº/ ,]+?:|$)",
            text,
        ):
            label = self._normalize_label(match.group(1))
            value = clean_text(match.group(2))
            if label and value:
                labels.setdefault(label, value)
        return labels

    def _normalize_label(self, label: str) -> str:
        return re.sub(r"[^a-z0-9 ]+", "", fold(clean_text(label))).strip()

    def _first_label(self, labels: dict[str, str], *names: str) -> str | None:
        normalized = [self._normalize_label(name) for name in names]
        for name in normalized:
            if labels.get(name):
                return labels[name]
        for key, value in labels.items():
            if any(name in key for name in normalized):
                return value
        return None

    def _extract_after(self, text: str, label: str) -> str | None:
        pattern = re.escape(label)
        match = re.search(pattern + r"\s*([^:]+?)(?=\s+[A-ZÁÉÍÓÚÜÑ][^:]{1,45}:|$)", text)
        return clean_text(match.group(1)) if match else None

    def _extract_local_id(self, text: str) -> str | None:
        match = re.search(
            r"N[ºo]\s*(?:de\s*)?[Aa]lerta:\s*([A-Z]{1,4}[\s_-]*\d+\s*/\s*\d{4})",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            return None
        value = clean_text(match.group(1)).upper().replace(" ", "_").replace("-", "_")
        return re.sub(r"_+", "_", value)

    def _canonical_id(self, local_id: str) -> str:
        return local_id.replace("/", "_")

    def _extract_lots(self, labels: dict[str, str], full_text: str) -> list[str]:
        value = self._first_label(labels, "lote", "lotes")
        if value:
            return self._split_values(value)
        matches = re.findall(r"\bLotes?:\s*([^:]+?)(?=\s+[A-ZÁÉÍÓÚÜÑ][^:]{1,45}:|$)", full_text)
        return self._split_values(" ".join(matches))

    def _split_values(self, value: str) -> list[str]:
        value = clean_text(value)
        if not value:
            return []
        parts = re.split(r"\s*(?:,|;|\by\b|\be\b|/)\s*", value, flags=re.IGNORECASE)
        return unique([part.strip(" .") for part in parts if part.strip(" .")])

    def _extract_recall_class(self, labels: dict[str, str], full_text: str) -> str | None:
        value = self._first_label(labels, "clasificacion de los defectos", "clasificacion")
        if value:
            class_match = re.search(r"\bClase\s*([123])\b", value, flags=re.IGNORECASE)
            return class_match.group(1) if class_match else value
        class_match = re.search(r"\bClase\s*([123])\b", full_text, flags=re.IGNORECASE)
        return class_match.group(1) if class_match else None

    def _extract_pdf_url(self, soup: BeautifulSoup, source_url: str) -> str | None:
        for link in soup.find_all("a", href=True):
            text = fold(clean_text(link.get_text(" ")))
            href = link["href"]
            if "pdf" in text or href.lower().endswith(".pdf"):
                return urljoin(source_url, href)
        return None

    def _needs_pdf_fallback(self, warnings: list[str]) -> bool:
        return any(item in warnings for item in ("missing_lots", "missing_reason", "missing_cn"))

    def _apply_pdf_fallback(self, pdf_url: str, warnings: list[str]) -> None:
        try:
            content = self.http.get_bytes(pdf_url)
            with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
                handle.write(content)
                handle.flush()
                text = self._extract_pdf_text(Path(handle.name))
            if text:
                warnings.append("pdf_fallback_checked")
        except Exception as exc:  # pragma: no cover - network/PDF dependent
            warnings.append(f"pdf_fallback_failed:{type(exc).__name__}")

    def _extract_pdf_text(self, path: Path) -> str:
        try:
            import pdfplumber
        except ImportError:
            return ""
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    def _confidence(self, warnings: list[str]) -> float:
        penalty = 0.08 * len([warning for warning in warnings if not warning.startswith("pdf_fallback")])
        return round(max(0.5, 1.0 - penalty), 2)
