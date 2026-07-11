<div align="center">
  <a href="https://github.com/mrueda/openrecall">
    <img src="docs-site/static/img/openrecall-logo.svg" width="220" alt="OpenRecall logo">
  </a>
  <p><em>Static medicine recall search from official public sources</em></p>
</div>

# OpenRecall

**OpenRecall: a static, country-extensible search index for pharmaceutical
recalls, starting with Spanish human-medicine recalls published by AEMPS.**

[![Build](https://github.com/mrueda/openrecall/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/mrueda/openrecall/actions/workflows/build-and-test.yml)
[![Documentation Status](https://github.com/mrueda/openrecall/actions/workflows/documentation.yml/badge.svg)](https://github.com/mrueda/openrecall/actions/workflows/documentation.yml)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://mrueda.github.io/openrecall/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<p align="center">
  <a href="https://mrueda.github.io/openrecall/app/">
    <strong>Open the live recall search app</strong>
  </a>
</p>

OpenRecall turns AEMPS recall pages and PDFs into normalized JSON datasets
that can be searched from a static website. The generated data can be hosted on
GitHub Pages without a backend, database server, account system, or cloud
runtime.

The first source adapter targets **Spain / AEMPS**. The schema, record IDs, and
data paths are country-aware so additional authorities such as FDA, MHRA,
Health Canada, and TGA can be added later through separate adapters.

OpenRecall is not a safety certification system. A missing search result
only means no matching recall was found in the indexed records. The public app
must not claim that a medicine is safe.

**Documentation:** <a href="https://mrueda.github.io/openrecall/" target="_blank">https://mrueda.github.io/openrecall/</a>

**Live Search App:** <a href="https://mrueda.github.io/openrecall/app/" target="_blank">https://mrueda.github.io/openrecall/app/</a>

**Quick Start:** <a href="https://mrueda.github.io/openrecall/docs/usage/quickstart" target="_blank">https://mrueda.github.io/openrecall/docs/usage/quickstart</a>

**Data Schema:** <a href="https://mrueda.github.io/openrecall/docs/technical-details/data-schema" target="_blank">https://mrueda.github.io/openrecall/docs/technical-details/data-schema</a>

**GitHub Repository:** <a href="https://github.com/mrueda/openrecall" target="_blank">https://github.com/mrueda/openrecall</a>

## Quick Start

Install locally from the repository root:

```bash
python3 -m pip install -e ".[test]"
```

Validate the bundled seed dataset:

```bash
python3 -m openrecall validate data
```

Build fresh recall data with the Python collector:

```bash
python3 -m openrecall build --output data
```

Build the static deploy directory:

```bash
python3 -m openrecall dist
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
```

Records use country-scoped identifiers such as `ES_AEMPS_R_21_2026`.
Spanish product codes are represented as structured entries:

```json
{"system": "CN", "value": "755215"}
```

Future countries can use their own national product-code systems without
changing the JSON field shape.

## Source Collection

The AEMPS adapter uses Python HTTP requests, retries, pagination, HTML parsing,
and transient PDF fallback parsing. It does not rely on `wget`, and it does not
commit downloaded PDFs.

The current source flow is:

- Discover candidates through the public AEMPS search endpoint.
- Use broad recall and year-qualified discovery queries.
- Parse AEMPS detail pages as the primary source.
- Accept human-medicine recall IDs such as `R_21/2026`.
- Reject veterinary alerts, cosmetics, product-safety notices, and general news.
- Write parser warnings and rejected candidates to `build-report.json`.

## Development

Run the Python test suite:

```bash
python3 -m pip install -e ".[test]"
pytest
```

Run bytecode and frontend checks:

```bash
python3 -m py_compile src/openrecall/*.py src/openrecall/adapters/*.py
node --check site/app.js
```

Validate static data:

```bash
python3 -m openrecall validate data
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

OpenRecall: static, country-extensible medicine recall search.
https://github.com/mrueda/openrecall

## Author

Written by Manuel Rueda.

Repository: <https://github.com/mrueda/openrecall>

## Copyright and License

Copyright (C) 2026 Manuel Rueda.

This project is distributed under the MIT License. See [LICENSE](LICENSE) for
details.
