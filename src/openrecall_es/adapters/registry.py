from __future__ import annotations

from openrecall_es.adapters.es_aemps import AempsSpainAdapter
from openrecall_es.http import HttpClient


def create_adapter(name: str, http: HttpClient, config: dict | None = None):
    if name == "es_aemps":
        return AempsSpainAdapter(http=http, start_year=(config or {}).get("backfill_start_year", 2020))
    raise ValueError(f"Unknown source adapter: {name}")


DEFAULT_SOURCES = ["es_aemps"]
