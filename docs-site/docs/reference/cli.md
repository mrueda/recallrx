# Command Line

This page is for developers and maintainers. Run commands from the repository
root after installing RecallRx in a virtual environment:

```bash
python3 -m pip install -e ".[test]"
```

## Update the Data

The default command performs an incremental build: it checks recent notices and
merges them with the records already in the output directory.

```bash
python3 -m recallrx build --output data --mode incremental
```

Available options:

- `--output PATH`: directory where the generated JSON files are written.
- `--source NAME`: run one source adapter. Repeat the option to select more than
  one source.
- `--mode incremental`: check recent or current-year entries and keep existing
  history. This is the default and the mode used by the daily workflow.
- `--mode full`: scan from `backfill_start_year` and replace records for the
  selected countries. Use it only for a deliberate historical rebuild.

## Validate the Data

```bash
python3 -m recallrx validate data
```

Validation checks required fields, country-scoped IDs, detail and summary
records, generated indexes, and the rule that downloaded PDFs must not be
committed.

## Read the Build Summary

```bash
python3 -m recallrx summary data
```

This prints the same Markdown table shown in the GitHub Actions job summary. It
reports possible notices found, accepted and rejected records, warnings,
retained history, and the net change for each country.

## Build the Static App

```bash
python3 -m recallrx dist
```

Available options:

- `--site PATH`: directory containing the static app source.
- `--data PATH`: directory containing generated data.
- `--output PATH`: directory where the deployable app is written.
