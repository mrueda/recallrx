# Troubleshooting

## The collector returns no records

Check whether AEMPS changed the search endpoint or result shape:

```bash
python3 -m openrecall_es build --output /tmp/openrecall-data
```

Then inspect the generated build report.

## The parser produces many warnings

Warnings usually mean AEMPS changed labels or table layout. Add a compact HTML
fixture under `tests/fixtures/` and update the parser with the new label
variant.

## The static app cannot load data

Build `dist/` and serve that directory rather than opening `site/index.html`
directly:

```bash
python3 -m openrecall_es dist
python3 -m http.server 8000 --directory dist
```

## Docusaurus search index is missing

Run the documentation build from `docs-site/`:

```bash
npm ci
npm run build
test -s build/search-index.json
```
