# Use the App

RecallRx is meant to start with the live search app. It is a static browser
search over daily exported medicine recall data from official sources:

<div className="button-row">
  <a className="button button--primary button--lg" href="https://mrueda.github.io/recallrx/app/">
    Open live search
  </a>
</div>

Use the search box to look for a medicine name, product code, lot, alert id, or
date. Use the country flags at the top of the app to switch between active
country datasets.

## What to Check

- Result title: medicine or recall title extracted from the official record.
- Product codes, lots, and manufacturer: normalized fields when the source
  provides them.
- Alert id and date: official reference information used for filtering.
- Source links: direct links back to the official page and PDF when available.
- Warnings: extraction notes that mean a human should verify the source record.
- Class and parser badges: hover or focus them to see short explanations.
- Export status and date: the latest daily static export for the selected
  country, with a visible warning when it is delayed or stale.

## Date Browsing

Use year chips for broad browsing and the date range fields for narrower review.
The app searches the indexed dataset only, so a missing result means no matching
record was found in the current RecallRx data.

## Color and Badge Cues

The header freshness indicator is teal when the latest export is less than 48
hours old, amber from 48 through 72 hours, and red after 72 hours or when the
timestamp is unavailable. Its hover text includes the exact export time and
selected authority.

The left card accent shows recall class only when the source publishes one:

- Red: class 1.
- Amber: class 2.
- Teal: class 3.
- Grey: no normalized class was published by the source.

Compact labels such as `Completo`, `Revisar`, `Sin CIP`, or match labels have
mouse-over and keyboard-focus explanations. These labels describe extraction
quality and search behavior; they are not medical advice.

## Developer Setup

Developer commands, local builds, and GitHub Actions are documented under
[For Developers](/docs/technical-details/architecture).
