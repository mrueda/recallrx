# Use the App

Start with the live search. You do not need an account and there is nothing to
install.

<div className="button-row">
  <a className="button button--primary button--lg" href="https://mrueda.github.io/recallrx/app/">
    Open live search
  </a>
</div>

## Search for a Notice

First choose a country using the buttons at the top of the app. Each country
has its own medicines authority and its own set of notices.

You can search for:

- a medicine or product name;
- a lot or batch number;
- an alert or recall number;
- a national product code, such as CN in Spain, AIM in Portugal, or CIP in
  France; or
- a year or date range.

You can combine a search term with the year and date filters. Clear the filters
when you want to return to all indexed notices for that country.

## Read a Result

A result may include the medicine name, notice date, alert number, affected
lots, product code, company, reason for the recall, and recall class. Authorities
do not always publish every field, so some results contain less detail than
others.

Use the source link on the result to open the original notice. A PDF link is
also shown when the authority provides one. The original notice is the record
to use when checking affected products or lots.

## Understand Labels and Colors

Small labels summarize information in the result. Hover over a label with a
mouse, or move keyboard focus to it, to read a short explanation.

- `Completo` means the expected details were found in the source.
- `Revisar` means some details were missing or could not be read reliably.
- `Sin CIP` means no French CIP product code was found in that notice.

When an authority publishes a recall class, the result uses a colored left
edge: red for class 1, amber for class 2, and teal for class 3. The class number
comes from the authority. RecallRx does not calculate it. A gray edge means no
class was available in the indexed notice.

## Check the Update Date

The top of the app shows when data for the selected country was last updated:

- `Actualizado`: updated less than 48 hours ago;
- `Actualización retrasada`: between 48 and 72 hours old;
- `Datos desactualizados`: more than 72 hours old; or
- `Datos no actualizados`: no valid update date is available.

Hover over the update status to see the exact time and authority. If the data
is delayed or out of date, check the authority's website for newer notices.

## If You Find No Match

Try the medicine name without the strength or package size, check the spelling
of the lot or product code, remove date filters, and confirm that the correct
country is selected.

No match means only that the current RecallRx data contains no matching indexed
notice. See [Limits and Safety](./safety-language.md) before drawing a conclusion
from an empty search.
