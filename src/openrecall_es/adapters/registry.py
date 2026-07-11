from __future__ import annotations

from openrecall_es.adapters.es_aemps import AempsSpainAdapter
from openrecall_es.http import HttpClient


def create_adapter(name: str, http: HttpClient):
    if name == "es_aemps":
        return AempsSpainAdapter(http=http)
    raise ValueError(f"Unknown source adapter: {name}")


DEFAULT_SOURCES = ["es_aemps"]
