# OpenRecall ES

## Overview

OpenRecall ES is an open-source, static web application that aggregates
and indexes Spanish pharmaceutical recalls published by AEMPS.

The project aims to make medicine recall information searchable by:

-   Medicine name
-   Código Nacional (CN)
-   Batch/Lot number
-   Recall ID
-   Recall date

The project is designed to be completely static:

-   No backend
-   No database server
-   No cloud infrastructure
-   Hosted entirely on GitHub Pages
-   Updated automatically every day via GitHub Actions

------------------------------------------------------------------------

# Motivation

Currently, AEMPS publishes pharmaceutical recalls as:

-   HTML pages
-   PDF documents

Although the information is public, it is difficult to search
programmatically.

OpenRecall ES converts these documents into structured JSON datasets.

------------------------------------------------------------------------

# Goals

## MVP

Users can search by:

-   Medicine name
-   CN (Código Nacional)
-   Lot number

For each recall, display:

-   Recall ID
-   Date
-   Recall class
-   Medicine name
-   Manufacturer
-   CN
-   Affected lots
-   Reason
-   Link to the original AEMPS document

Display:

-   Last dataset update
-   Data source
-   Search confidence

Never display:

> "This product is safe."

Instead display:

> "No matching recall was found in the indexed AEMPS records."

------------------------------------------------------------------------

# Architecture

``` text
AEMPS
    │
    ▼
GitHub Actions (daily)
    │
    ├── Download alert index
    ├── Download PDFs
    ├── Parse PDFs
    ├── Normalize
    ├── Validate
    └── Generate JSON
            │
            ▼
GitHub Pages
            │
            ▼
Static Search Website
```

------------------------------------------------------------------------

# Repository Layout

``` text
openrecall-es/

├── src/
│   ├── fetch.py
│   ├── parse.py
│   ├── normalize.py
│   ├── build_index.py
│   └── validators.py
│
├── data/
│   ├── metadata.json
│   ├── recalls-summary.json
│   ├── recalls/
│   ├── by-cn/
│   └── by-year/
│
├── site/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── assets/
│
├── tests/
│
└── .github/
    └── workflows/
        ├── update.yml
        └── deploy.yml
```

------------------------------------------------------------------------

# Daily Workflow

1.  Fetch AEMPS alert index.
2.  Detect new recalls.
3.  Download new PDFs.
4.  Parse relevant fields.
5.  Validate extracted data.
6.  Generate normalized JSON.
7.  Commit updated dataset.
8.  Deploy GitHub Pages.

Support manual execution using `workflow_dispatch`.

------------------------------------------------------------------------

# Data Model

``` json
{
  "id": "R_21_2026",
  "date": "2026-06-04",
  "class": 2,
  "medicine": "...",
  "manufacturer": "...",
  "cn": ["755215"],
  "lots": ["ABC123", "ABC124"],
  "reason": "...",
  "source": "...",
  "pdf": "..."
}
```

------------------------------------------------------------------------

# JSON Strategy

Generate:

``` text
metadata.json

recalls-summary.json

recalls/
    R_21_2026.json
    R_22_2026.json

by-cn/
    755215.json

by-year/
    2024.json
    2025.json
    2026.json
```

Load the summary index first, then fetch detailed records on demand.

------------------------------------------------------------------------

# Search

Support:

-   Exact CN search
-   Exact lot search
-   Exact recall ID search
-   Fuzzy medicine name search
-   Fuzzy manufacturer search

Suggested libraries:

-   MiniSearch
-   Fuse.js

------------------------------------------------------------------------

# Technology Stack

-   Frontend: HTML, CSS, Vanilla JavaScript
-   Hosting: GitHub Pages
-   Automation: GitHub Actions
-   Parsing: Python + BeautifulSoup + pdfplumber (or equivalent)
-   Output: JSON
-   License: MIT

------------------------------------------------------------------------

# Future Features

## GS1 DataMatrix support

Workflow:

``` text
Phone camera
        │
        ▼
Decode GS1 DataMatrix
        │
        ▼
Extract:
- GTIN
- Lot
- Expiry
- Serial
        │
        ▼
Map GTIN → Código Nacional → Recall lookup
```

## CIMA Integration

Enrich recalls with:

-   Active ingredient
-   ATC code
-   Dosage form
-   Manufacturer
-   Product metadata

## International Expansion

Future collectors:

-   Spain (AEMPS)
-   FDA (USA)
-   MHRA (UK)
-   Health Canada
-   TGA (Australia)

using the same normalized schema.

------------------------------------------------------------------------

# Non-Goals

Do not build:

-   User accounts
-   Authentication
-   Server-side API
-   Database server
-   Admin panel

The project should remain fully static and deployable through GitHub
Pages.

------------------------------------------------------------------------

# Vision

Create an open-source, searchable, versioned database of pharmaceutical
recalls based on official public sources.

Start with Spain, then expand internationally while remaining
transparent, reproducible, and easy to contribute to.
