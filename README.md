# OpenRecall ES

OpenRecall ES is a static, country-extensible recall index for medicines.
The first source adapter indexes Spanish human-medicine recalls published by
AEMPS and writes static JSON that can be searched from GitHub Pages.

## Commands

```bash
python3 -m openrecall_es build --output data
python3 -m openrecall_es validate data
python3 -m openrecall_es dist
python3 -m http.server 8000 --directory dist
```

The build command uses Python HTTP requests, retries, HTML parsing, and PDF
fallback parsing. PDFs are downloaded only to temporary storage and are not
committed.

## Data Layout

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

## Documentation

The Docusaurus documentation site lives in `docs-site/`.

```bash
cd docs-site
npm ci
npm run typecheck
npm run build
```
