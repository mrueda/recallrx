# Country Collectors

A source adapter is the Python code that collects and reads notices from one
medicines authority. Keeping authority-specific code in separate adapters lets
RecallRx add countries without changing the shared data writer or search app.

The active adapters are:

| Adapter | Country | Authority |
| --- | --- | --- |
| `es_aemps` | Spain | AEMPS |
| `pt_infarmed` | Portugal | INFARMED |
| `fr_ansm` | France | ANSM |

## Shared Contract

Every adapter declares its `country` and `authority` and provides a `build()`
method. That method returns RecallRx records plus a report describing accepted,
rejected, and incomplete results.

An adapter can organize its work as needed, but most follow four steps:
discovery, download, parsing, and conversion to the shared record format.

All active adapters support the shared collection mode and
`backfill_start_year` setting.

## How Discovery Differs by Country

- AEMPS uses its public search service. Incremental mode searches the current
  year; full mode searches the configured range of years.
- INFARMED uses recent Alertas pages for daily updates and its historical
  human-medicine search for full builds. Duplicate content and PDF results are
  merged. If an older detail page fails, the official search summary can be
  retained with a warning and lower confidence.
- ANSM uses its medicine product-recall listings and filters them by year.

These differences stay inside the adapters. The generated files use the same
paths and fields for every country.

## Add a Country

1. Create an adapter under `src/recallrx/adapters/`.
2. Convert its results to the shared `RecallRecord` model.
3. Register the adapter in the source registry.
4. Add small, representative source fixtures and parser tests.
5. Add country metadata and user-interface text when the source is ready for
   the public app.

Do not enable a country based only on a successful one-off scrape. Confirm that
the source supports repeatable discovery, stable links, historical coverage,
and enough detail to identify affected medicines or lots.
