# Quick Start

Install the Python package locally from the repository root:

```bash
python3 -m pip install -e ".[test]"
```

Validate the bundled seed dataset:

```bash
python3 -m openrecall_es validate data
```

Build fresh data with the Python collector:

```bash
python3 -m openrecall_es build --output data
```

Build the static deploy directory:

```bash
python3 -m openrecall_es dist
```

Serve the static app locally:

```bash
python3 -m http.server 8000 --directory dist
```

Run tests:

```bash
pytest
node --check site/app.js
```

Build the documentation site:

```bash
cd docs-site
npm ci
npm run typecheck
npm run build
```
