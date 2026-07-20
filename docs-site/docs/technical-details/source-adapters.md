# Source Adapters

Source adapters isolate country-specific discovery and parsing from the shared
dataset writer.

Active adapters are:

- `es_aemps`
- `pt_infarmed`
- `fr_ansm`

## Adapter contract

An adapter provides:

- `country`
- `authority`
- `build()`

The `build()` method returns normalized recall records and a build report.
Internally, adapters may split this into discovery, fetch, parse, and normalize
steps.

Every active adapter accepts the shared collection mode and
`backfill_start_year`. Incremental discovery is deliberately bounded to recent
or current-year records. Full discovery uses authority-specific historical
searches:

- AEMPS: current-year or multi-year WordPress/API discovery.
- INFARMED: recent Alertas pages or the human-medicine historical search, with
  content/PDF result deduplication. If an older detail route fails, a lower-
  confidence record is retained from the official search summary and marked
  for review; year-organized archived circulars are the corroboration source.
- ANSM: filtered medicine product-recall listings, queried by year.

## Adding a country

To add a new source:

1. Create a new adapter under `src/recallrx/adapters/`.
2. Normalize records into the shared `RecallRecord` model.
3. Add the adapter to the source registry.
4. Add fixtures and tests for source-specific parsing.
5. Add country metadata and UI labels only if the country should be enabled in
   the public app.

The shared JSON paths are already country-aware:

```text
data/countries/es/
data/countries/pt/
data/countries/fr/
data/countries/ad/
```
