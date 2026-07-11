# Overview

OpenRecall is a static, open-source index of medicine recalls from official
public sources. The first source is Spain's AEMPS, and the code is structured
so additional countries can be added through source adapters.

<div className="button-row">
  <a className="button button--primary button--lg" href="/openrecall/app">
    Open the live recall search app
  </a>
</div>

The project converts recall pages and PDFs into normalized JSON datasets that
can be searched from a static website. It does not require a backend, database
server, account system, or cloud runtime.

## Current capabilities

- Python collector for AEMPS search and recall detail pages.
- HTML-first parsing with transient PDF fallback when required fields are
  missing.
- Country-aware normalized recall schema.
- Static JSON output for GitHub Pages.
- Browser search over medicine name, product code, lot, recall id, and reason.
- GitHub Actions for tests, data updates, and documentation builds.

## Non-goals

- Safety certification or product safety claims.
- User accounts, authentication, or an admin panel.
- Server-side APIs or hosted databases.
- CIMA enrichment, GS1 DataMatrix scanning, or international collectors in the
  first MVP.

## Trust model

OpenRecall indexes official records. Every result must link back to the
original source page and PDF when available. A missing result only means no
matching record was found in the indexed dataset.
