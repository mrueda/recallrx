# CLI Reference

Run commands from the repository root.

## Build data

```bash
python3 -m openrecall build --output data
```

Options:

- `--output PATH`: output directory for generated JSON.
- `--source NAME`: source adapter to run. Can be supplied more than once.

## Validate data

```bash
python3 -m openrecall validate data
```

Validation checks required fields, country-scoped ids, detail records, summary
records, indexes, and that PDFs were not committed.

## Build static app

```bash
python3 -m openrecall dist
```

Options:

- `--site PATH`: static app source directory.
- `--data PATH`: generated data directory.
- `--output PATH`: deployable output directory.
