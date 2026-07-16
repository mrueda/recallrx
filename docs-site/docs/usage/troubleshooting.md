# Troubleshooting

## The collector returns no records

Check whether the relevant authority changed its search endpoint, listing page,
or result shape:

```bash
python3 -m recallrx build --output /tmp/recallrx-data
```

Then inspect the generated build report.

## The parser produces many warnings

Warnings usually mean a source page changed labels or table layout, or that the
authority did not publish a structured field in that notice. Add a compact HTML
fixture under `tests/fixtures/` and update the relevant adapter with the new
label variant.

## The static app cannot load data

Build `dist/` and serve that directory rather than opening `site/index.html`
directly:

```bash
python3 -m recallrx dist
python3 -m http.server 8000 --directory dist
```

## Docusaurus search index is missing

Run the documentation build from `docs-site/`:

```bash
npm ci
npm run build
test -s build/search-index.json
```
