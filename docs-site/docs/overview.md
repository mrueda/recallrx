# Start Here

RecallRx helps you find medicine recall notices published by national medicines
authorities. It brings notices from Spain, Portugal, and France into one search
app and links each result back to the authority that published it.

<div className="button-row">
  <a className="button button--primary button--lg" href="https://mrueda.github.io/recallrx/app/">
    Open the live search
  </a>
</div>

## What You Can Do

1. Choose Spain, Portugal, or France at the top of the app.
2. Search for a medicine name, product code, lot number, alert number, year, or
   date range.
3. Open a result to check the notice on the authority's website.

RecallRx currently uses notices from AEMPS in Spain, INFARMED in Portugal, and
ANSM in France. The data is normally refreshed once a day. The app shows the
date and status of the latest update for the country you selected.

## Before You Rely on a Result

RecallRx is an index of published notices, not a medical advice service. A
search with no results means only that RecallRx did not find a match in its
current data. It does not prove that a medicine is safe or unaffected.

Check the official source linked from the result before making a decision. If
you need advice about a medicine you are using, speak to a pharmacist, doctor,
or the relevant medicines authority.

## Choose the Right Guide

- [Use the App](./usage/quickstart.md) explains searches, filters, labels, and
  update dates.
- [Limits and Safety](./usage/safety-language.md) explains what a result can and
  cannot tell you.
- [Help with the App](./usage/troubleshooting.md) covers missing results, stale
  data, and display problems.
- [Architecture](./technical-details/architecture.md) is the starting point for
  developers and maintainers.

## What RecallRx Does Not Do

RecallRx does not provide medical advice, certify product safety, rank the
seriousness of a notice, or accept user-submitted recall reports. It does not
replace the original notice published by an authority.
