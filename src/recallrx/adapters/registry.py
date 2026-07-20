from __future__ import annotations

from recallrx.adapters.es_aemps import AempsSpainAdapter
from recallrx.adapters.fr_ansm import AnsmFranceAdapter
from recallrx.adapters.pt_infarmed import InfarmedPortugalAdapter
from recallrx.http import HttpClient


def create_adapter(name: str, http: HttpClient, config: dict | None = None, mode: str = "incremental"):
    start_year = (config or {}).get("backfill_start_year", 2020)
    if name == "es_aemps":
        return AempsSpainAdapter(http=http, start_year=start_year, mode=mode)
    if name == "pt_infarmed":
        return InfarmedPortugalAdapter(http=http, start_year=start_year, mode=mode)
    if name == "fr_ansm":
        return AnsmFranceAdapter(http=http, start_year=start_year, mode=mode)
    raise ValueError(f"Unknown source adapter: {name}")


DEFAULT_SOURCES = ["es_aemps", "pt_infarmed", "fr_ansm"]
