# Operations

RecallRx is designed to run as a scheduled static data pipeline.

## Daily update

The documentation workflow runs daily. It builds a fresh static export from all
enabled country adapters, validates the generated JSON, embeds the browser app,
builds Docusaurus, and deploys the resulting static site to GitHub Pages.

```bash
python -m recallrx build --output data
python -m recallrx validate data
```

The collectors use Python HTTP requests rather than `wget`, so they can set a
clear user agent, retry transient failures, page through authority search
results, parse HTML, and fall back to PDFs when needed.

## Deployment

The live app is embedded into the Docusaurus site at `/app/`. The docs build
runs `python -m recallrx dist --output docs-site/static/app`, then builds the
site. The timestamp shown as "Exportación diaria" comes from the generated
country metadata.

## Manual checks

When a scheduled update changes many records, inspect:

- `data/countries/<country>/build-report.json`
- rejected candidate counts
- parser warnings on accepted records
- changes to `recalls-summary.json`
- any new missing product-code, lot, date, or reason fields
