<div align="center">
  <a href="https://github.com/mrueda/recallrx">
    <img src="docs-site/static/img/recallrx-logo.svg" width="220" alt="RecallRx logo">
  </a>
  <p><em>Static medicine recall search from official public sources</em></p>
</div>

# RecallRx

**RecallRx: a static, country-aware search app for medicine recalls from
official public sources.**

[![Build](https://github.com/mrueda/recallrx/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/mrueda/recallrx/actions/workflows/build-and-test.yml)
[![Documentation Status](https://github.com/mrueda/recallrx/actions/workflows/documentation.yml/badge.svg)](https://github.com/mrueda/recallrx/actions/workflows/documentation.yml)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://mrueda.github.io/recallrx/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<p align="center">
  <a href="https://mrueda.github.io/recallrx/app/">
    <strong>Open the live recall search app</strong>
  </a>
</p>

RecallRx turns official medicine recall notices into normalized JSON datasets
that can be searched from a static website. The generated app can be hosted on
GitHub Pages without a backend, database server, account system, or cloud
runtime.

The active datasets are currently **Spain / AEMPS**, **Portugal / INFARMED**,
and **France / ANSM**. The app, schema, record IDs, and data paths are
country-aware, and the live interface already exposes a planned country slot for
**Andorra / Ministeri de Salut**. Additional authorities are added through
separate source adapters without changing the browser search contract.

RecallRx is not a safety certification system. A missing search result
only means no matching recall was found in the indexed records. The public app
must not claim that a medicine is safe.

**Documentation:** <a href="https://mrueda.github.io/recallrx/" target="_blank">https://mrueda.github.io/recallrx/</a>

**Live Search App:** <a href="https://mrueda.github.io/recallrx/app/" target="_blank">https://mrueda.github.io/recallrx/app/</a>

**Quick Start:** <a href="https://mrueda.github.io/recallrx/docs/usage/quickstart" target="_blank">https://mrueda.github.io/recallrx/docs/usage/quickstart</a>

**Data Schema:** <a href="https://mrueda.github.io/recallrx/docs/technical-details/data-schema" target="_blank">https://mrueda.github.io/recallrx/docs/technical-details/data-schema</a>

**GitHub Repository:** <a href="https://github.com/mrueda/recallrx" target="_blank">https://github.com/mrueda/recallrx</a>

## Quick Start

Install locally from the repository root:

```bash
python3 -m pip install -e ".[test]"
```

Validate the bundled seed dataset:

```bash
python3 -m recallrx validate data
```

Build fresh recall data with the Python collector:

```bash
python3 -m recallrx build --output data
```

Build the static deploy directory:

```bash
python3 -m recallrx dist
```

Serve the static app locally:

```bash
python3 -m http.server 8000 --directory dist
```

## Data

Generated data is written as static JSON:

```text
data/
  metadata.json
  countries/
    es/
      metadata.json
      recalls-summary.json
      recalls/
      by-code/
      by-year/
      build-report.json
    pt/
    fr/
    ad/
```

Records use country-scoped identifiers such as `ES_AEMPS_R_21_2026`.
Product codes are represented as structured entries, so each country can keep
its own code system:

```json
{"system": "CN", "value": "755215"}
```

Spain currently uses `CN`, Portugal uses INFARMED registration numbers as
`AIM`, and France uses `CIP` without changing the JSON field shape.

## Source Collection

Each country source is implemented as an adapter. Adapters use Python HTTP
requests, retries, pagination, structured APIs or HTML parsing where available,
and transient PDF fallback parsing when useful. They do not rely on `wget`, and
they do not commit downloaded PDFs.

The current Spain / AEMPS source flow is:

- Discover candidates through the public AEMPS WordPress posts API, with the
  AEMPS search endpoint as fallback.
- Use a configurable backfill start year.
- Parse AEMPS detail pages as the primary source.
- Accept human-medicine recall IDs such as `R_21/2026`.
- Reject veterinary alerts, cosmetics, product-safety notices, and general news.
- Write parser warnings and rejected candidates to `build-report.json`.

The current Portugal / INFARMED source flow is:

- Discover candidates from the official paginated INFARMED Alertas listing.
- Accept medicine recall and withdrawal notices marked as `Tipo de alerta: med`.
- Reject cosmetic and device alerts even when their titles mention withdrawal.
- Parse circular IDs, dates, medicine names, INFARMED registration numbers,
  lots, expiry dates, manufacturers, reasons, and actions from the detail page.
- Write parser warnings and rejected candidates to `build-report.json`.

The current France / ANSM source flow is:

- Discover candidates from the official paginated ANSM information-safety list.
- Accept entries marked as `RAPPEL DE PRODUIT` and `Médicaments`.
- Reject device, diagnostic, cosmetic, and other non-medicine recalls.
- Parse publication dates, medicine names, manufacturers, CIP codes, lots,
  expiry dates, reasons, and recall-level text from the detail page.
- Write parser warnings and rejected candidates to `build-report.json`.

Daily GitHub Pages deployments rebuild fresh recall data before publishing the
static app. The workflow can also be run manually from GitHub Actions.

## Development

Run the Python test suite:

```bash
python3 -m pip install -e ".[test]"
pytest
```

Run bytecode and frontend checks:

```bash
python3 -m py_compile src/recallrx/*.py src/recallrx/adapters/*.py
node --check site/app.js
```

Validate static data:

```bash
python3 -m recallrx validate data
```

Run the docs checks:

```bash
cd docs-site
npm ci
npm run typecheck
npm run build
```

## Citation

No formal citation is available yet. For now, cite the GitHub repository:

RecallRx: static, country-extensible medicine recall search.
https://github.com/mrueda/recallrx

## Author

Written by Manuel Rueda.

Repository: <https://github.com/mrueda/recallrx>

## Copyright and License

Copyright (C) 2026 Manuel Rueda.

This project is distributed under the MIT License. See [LICENSE](LICENSE) for
details.
