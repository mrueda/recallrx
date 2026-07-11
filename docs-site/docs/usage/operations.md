# Operations

OpenRecall is designed to run as a scheduled static data pipeline.

## Daily update

The dataset update workflow runs the Python collector, validates the generated
JSON, and commits changes only when the `data/` directory changes.

```bash
python -m openrecall build --output data
python -m openrecall validate data
```

The collector uses Python HTTP requests rather than `wget`, so it can set a
clear user agent, retry transient failures, page through AEMPS search results,
parse HTML, and fall back to PDFs when needed.

## Deployment

The application deployment workflow builds `dist/` from `site/` and `data/`.
The documentation workflow builds `docs-site/` separately so docs can be
validated without replacing the search app deployment.

## Manual checks

When a scheduled update changes many records, inspect:

- `data/countries/es/build-report.json`
- rejected candidate counts
- parser warnings on accepted records
- changes to `recalls-summary.json`
- any new missing `CN`, lot, date, or reason fields
