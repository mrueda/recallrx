# Overview

RecallRx is a live search app for medicine recalls indexed from official
public sources. Start with the app, then use these docs when you need to
understand the results or maintain the dataset.

<div className="button-row">
  <a className="button button--primary button--lg" href="https://mrueda.github.io/recallrx/app/">
    Open the live recall search app
  </a>
</div>

The active sources are Spain/AEMPS, Portugal/INFARMED, and France/ANSM. The app
and data model are country-aware, so additional authorities can be added without
changing how users search.

## For Users

- Search by medicine name, product code, lot, alert id, year, or date range.
- Switch countries from the app header.
- Open official source pages and PDFs from every result when available.
- Treat warnings as a prompt to verify the original record.

RecallRx is an index. It does not replace advice from health authorities,
clinicians, pharmacists, or official product notices.

## For Developers

- Python collectors for official country authority pages.
- HTML-first parsing with transient PDF fallback when required fields are
  missing.
- Country-aware normalized recall schema.
- Static JSON output for GitHub Pages.
- Static browser app over medicine name, product code, lot, recall id, reason,
  and dates.
- Manual GitHub Actions for tests and daily documentation/data builds.

## Non-goals

- Safety certification or product safety claims.
- User accounts, authentication, or an admin panel.
- Server-side APIs or hosted databases.
- Safety scoring, product recommendations, or user-submitted medical advice.

## Trust model

RecallRx indexes official records. Every result must link back to the
original source page and PDF when available. A missing result only means no
matching record was found in the indexed dataset.
