# Architecture

This page is for developers and maintainers. RecallRx does not use an
application server or database. Python code collects public notices and writes
JSON files; the browser downloads those files and searches them locally.

<div className="dataFlow">
  <span>Authority websites</span>
  <span>Country collectors</span>
  <span>JSON data files</span>
  <span>Browser search</span>
  <span>GitHub Pages</span>
</div>

## Collecting Notices

Each medicines authority has its own website and document format. RecallRx
keeps the code for one authority in a source adapter, also called a country
collector. An adapter:

1. finds possible recall notices;
2. downloads the relevant pages or documents;
3. reads the fields provided by that authority; and
4. converts the result to the common RecallRx data format.

The source registry tells the command-line tool which adapters are enabled. A
build report records how many possible notices were found, accepted, rejected,
or accepted with warnings.

## Incremental and Full Builds

An incremental build is the normal daily update. It checks recent or
current-year listings, adds new records, updates changed records, and keeps
older records already stored in the country dataset.

A full build is a deliberate historical scan. It starts at the configured
`backfill_start_year` and replaces the data for the countries being rebuilt.
Countries not selected with `--source` are left unchanged in both modes.

Records are matched by their stable RecallRx ID and source URL. This prevents a
notice from disappearing merely because an authority removes it from a recent
notices page.

## Data Used by the App

The frontend reads three main files:

- `data/metadata.json`: available countries and the overall build time;
- `data/countries/<country>/metadata.json`: authority and update information
  for one country; and
- `data/countries/<country>/recalls-summary.json`: the searchable list of
  recall records.

The app first looks for exact product-code, lot, and recall-ID matches. It then
uses text search for names, manufacturers, reasons, and other words.

## Documentation and Deployment

The search app lives in `site/`. The Docusaurus project lives in `docs-site/`.
During deployment, the build command copies the app and current data into
`docs-site/static/app`, then Docusaurus publishes the documentation and app as
one GitHub Pages site.

Keeping the source directories separate allows the app, data generation, and
documentation to be tested independently.

Only `.github/workflows/deploy.yml` deploys Pages. It uploads the whole
`docs-site/build` directory as one artifact. This ensures that the docs and app
always come from the same build, even though CI tests can run in a separate
workflow.

`.github/workflows/documentation.yml` is an independent manual check. It
performs the same documentation type-check and production build without Pages
permissions, artifact deployment, or a dependency on `deploy.yml`.
