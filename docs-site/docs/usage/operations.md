# Updates and Deployment

This page is for maintainers. RecallRx has two independent documentation-related
GitHub Actions workflows:

- `documentation.yml` is a manual validation workflow. It type-checks and
  builds the docs and embedded app, but it cannot deploy Pages.
- `deploy.yml` builds and publishes both the documentation and the app. It is
  the only workflow with Pages permissions.

Neither workflow calls or waits for the other. Every deployment still uploads
the docs and app together as one artifact, so one cannot replace the other on
the live site.

## Daily Update

The deployment workflow runs once a day in incremental mode. It:

1. checks the recent or current-year listings for every enabled authority;
2. adds new notices and updates existing ones while keeping older records;
3. validates all generated JSON;
4. copies the search app into the documentation site;
5. builds Docusaurus; and
6. deploys the result to GitHub Pages.

The equivalent local data commands are:

```bash
python3 -m recallrx build --output data --mode incremental
python3 -m recallrx validate data
```

When recall details change, the workflow commits the updated `data/` directory.
If only the export time changes, the site is redeployed without creating a data
commit. Older records remain available even after an authority removes them
from a recent-notices page.

The same workflow also runs after a relevant change reaches `main`. A docs
change is deployed with the current app; an app or data change is deployed with
the current docs. Push-triggered runs use the committed data and do not contact
the authority websites. Scheduled and manually started runs perform data
collection before building the site.

## Build Summary

Each workflow run includes a country-by-country summary:

- collected: possible notices found at the source;
- accepted: notices written to the dataset;
- rejected: results that were not valid medicine recalls;
- warnings: accepted records that need review;
- retained: existing historical records kept during the update; and
- net: the change in the number of records.

Generate the same summary locally with:

```bash
python3 -m recallrx summary data
```

## Historical Backfill

A full historical build is a manual operation:

```bash
python3 -m recallrx build --output data --mode full
python3 -m recallrx validate data
```

Full mode scans from `backfill_start_year` and replaces the data for the
selected countries. It is also available from the workflow's manual-run form.

Some older Portuguese records carry a `source_detail_fallback` warning. Their
INFARMED detail page did not respond, so the collector used the official search
summary instead. These records should be checked against INFARMED's archived
"Anos anteriores (Alertas)" circulars when more detail is needed.

The collectors use Python HTTP requests rather than `wget`. This allows them to
identify RecallRx with a user agent, retry temporary failures, follow paginated
results, parse HTML, and inspect a PDF when required fields are missing.

## Deployment and Freshness

The live app is published at `/app/` inside the Docusaurus site. The docs build
runs:

```bash
python3 -m recallrx dist --output docs-site/static/app
```

Docusaurus then builds `docs-site/build`. That complete directory is the only
artifact passed to GitHub Pages. Do not add a second Pages workflow for the app:
each Pages deployment replaces the whole published site, so separate app and
docs deployments could overwrite one another.

The update time shown in the app comes from each country's generated metadata.
The status changes to delayed after 48 hours and out of date after 72 hours. A
failed update is therefore visible while the last valid dataset remains online.

## Common Failures

### A collector returns no records

The authority may have changed its search address, page layout, or result
format. Run a build for the affected source and inspect its generated
`build-report.json` before changing the adapter.

### A collector produces many warnings

Compare the affected source pages with the adapter's fixtures. Add a small HTML
fixture for a real new layout or label, then update the adapter and its tests.
Do not hide warnings by making a field optional unless the authority genuinely
omits that field.

### The local app cannot load data

Build and serve `dist/` instead of opening `site/index.html` directly:

```bash
python3 -m recallrx dist
python3 -m http.server 8000 --directory dist
```

### The Docusaurus search index is missing

Run the production documentation build from `docs-site/`:

```bash
npm ci
npm run build
test -s build/search-index.json
```

Local development does not enable the production search plugin, so use the
production build when testing the generated search index.

## Review a Large Update

When a run changes many records, inspect:

- `data/countries/<country>/build-report.json`;
- rejected and warning counts;
- the diff for `recalls-summary.json`;
- new missing product-code, lot, date, or reason fields; and
- unexpected changes to the total count for an unaffected country.

Public wording must never turn an empty search into a safety claim. Use phrases
such as "no matching notice in the indexed data," and keep the official source
link visible on every result.
