# Architecture

OpenRecall has two static outputs: the recall search app and this
documentation site.

<div className="dataFlow">
  <span>AEMPS</span>
  <span>Python adapter</span>
  <span>Normalized JSON</span>
  <span>Static search UI</span>
  <span>GitHub Pages</span>
</div>

## Collector pipeline

The Python CLI loads enabled source adapters from the registry. Each adapter
discovers candidate records, fetches source pages, parses source-specific
fields, normalizes them into the shared schema, and returns build diagnostics.

## Static search app

The frontend reads:

- `data/metadata.json`
- `data/countries/<country>/metadata.json`
- `data/countries/<country>/recalls-summary.json`

The app uses exact matching for product codes, lots, and recall ids before
falling back to fuzzy text search.

## Documentation site

The Docusaurus site lives in `docs-site/` and builds independently from the
recall search app. This keeps product documentation testable without changing
the data deployment path.
