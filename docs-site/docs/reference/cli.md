# CLI Reference

Run commands from the repository root.

## Build data

```bash
python3 -m recallrx build --output data --mode incremental
```

Options:

- `--output PATH`: output directory for generated JSON.
- `--source NAME`: source adapter to run. Can be supplied more than once.
- `--mode incremental`: collect recent/current-year entries and merge them into
  records already under `--output`. This is the default and scheduled mode.
- `--mode full`: scan from `backfill_start_year` and replace records for the
  selected source countries. Use this for deliberate historical backfills.

## Validate data

```bash
python3 -m recallrx validate data
```

Validation checks required fields, country-scoped ids, detail records, summary
records, indexes, and that PDFs were not committed.

## Build static app

```bash
python3 -m recallrx dist
```

Options:

- `--site PATH`: static app source directory.
- `--data PATH`: generated data directory.
- `--output PATH`: deployable output directory.
