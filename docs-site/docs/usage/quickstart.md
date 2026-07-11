# Use the App

OpenRecall is meant to start with the live search app:

<div className="button-row">
  <a className="button button--primary button--lg" href="https://mrueda.github.io/openrecall/app/">
    Open live search
  </a>
</div>

Use the search box to look for a medicine name, product code, lot, alert id, or
date. Use the country flags at the top of the app to switch datasets when more
countries are available.

## What to Check

- Result title: medicine or recall title extracted from the official record.
- CN, lots, and manufacturer: normalized fields when the source provides them.
- Alert id and date: official reference information used for filtering.
- Source links: direct links back to the official page and PDF when available.
- Warnings: extraction notes that mean a human should verify the source record.

## Date Browsing

Use year chips for broad browsing and the date range fields for narrower review.
The app searches the indexed dataset only, so a missing result means no matching
record was found in the current OpenRecall data.

## Developer Setup

Developer commands, local builds, and GitHub Actions are documented under
[For Developers](/docs/technical-details/architecture).
