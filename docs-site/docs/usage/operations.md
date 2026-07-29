# Operations

RecallRx is designed to run as a scheduled static data pipeline.

## Daily update

The documentation workflow runs daily in incremental mode. It checks the recent
or current-year views of all enabled authorities, merges new and updated records
into retained history, validates the generated JSON, embeds the browser app,
builds Docusaurus, and deploys the result to GitHub Pages.

```bash
python -m recallrx build --output data --mode incremental
python -m recallrx validate data
```

When recall details change, the workflow commits the updated `data/` tree. This
retains records after they leave an authority's recent listing. A daily run with
no substantive record changes still publishes a current export timestamp but
does not create a data commit.

Each run writes a Markdown job summary with collected, accepted, rejected,
warning, retained, and net record counts for every updated country. Generate
the same summary locally with:

```bash
python -m recallrx summary data
```

## Historical backfill

Historical collection is an explicit operator action, not a daily task:

```bash
python -m recallrx build --output data --mode full
python -m recallrx validate data
```

Full mode scans from `backfill_start_year` and replaces data for the selected
source countries. The GitHub Actions manual-run form also exposes this mode.
Portuguese historical records marked `source_detail_fallback` came from an
official INFARMED search summary because its older detail route did not respond;
operators can corroborate them in INFARMED's "Anos anteriores (Alertas)"
circular archive.

The collectors use Python HTTP requests rather than `wget`, so they can set a
clear user agent, retry transient failures, page through authority search
results, parse HTML, and fall back to PDFs when needed.

## Deployment

The live app is embedded into the Docusaurus site at `/app/`. The docs build
runs `python -m recallrx dist --output docs-site/static/app`, then builds the
site. The timestamp shown as "Exportación diaria" comes from the generated
country metadata. The app marks exports as delayed after 48 hours and stale
after 72 hours, so a failed update remains visible while the previous static
dataset stays available.

## Manual checks

When an update changes many records, inspect:

- `data/countries/<country>/build-report.json`
- rejected candidate counts
- parser warnings on accepted records
- changes to `recalls-summary.json`
- any new missing product-code, lot, date, or reason fields
