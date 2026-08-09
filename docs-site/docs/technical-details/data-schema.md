# Data Format

Authorities publish different fields and use different names for them.
RecallRx converts each accepted notice to the same JSON structure so the app
can search every supported country in the same way.

Each record belongs to one country and authority. The country prefix in the ID
prevents two authorities from creating the same RecallRx ID.

```json
{
  "id": "ES_AEMPS_R_21_2026",
  "country": "ES",
  "authority": "AEMPS",
  "local_id": "R_21/2026",
  "date": "2026-06-03",
  "medicine": "OCULOTECT 50 mg/ml COLIRIO EN SOLUCION",
  "product_codes": [
    {"system": "CN", "value": "755215"}
  ],
  "lots": ["ABC123"],
  "source_url": "https://www.aemps.gob.es/...",
  "pdf_url": "https://www.aemps.gob.es/...",
  "confidence": 0.84,
  "warnings": []
}
```

## Field Groups

<div className="schemaGrid">
  <div className="schemaPill"><strong>Identity</strong>country, authority, id, local_id</div>
  <div className="schemaPill"><strong>Medicine</strong>medicine, manufacturer, product_codes, lots</div>
  <div className="schemaPill"><strong>Source and quality</strong>source_url, pdf_url, confidence, warnings</div>
</div>

`local_id` is the reference used by the authority. `source_url` points to its
public page, while `pdf_url` points to the original document when one is
available.

## Product Codes

The `product_codes` array keeps both the code and the national code system:

```json
{"system": "CN", "value": "755215"}
```

Current datasets use CN for Spain, AIM for Portugal, and CIP for France. A new
country can use its own code system without changing the JSON structure.

## Confidence and Warnings

`confidence` describes how reliably the collector read the fields from the
source. It is a data-extraction score, not a measure of clinical risk or recall
severity.

`warnings` explain missing fields or fallbacks used during collection. The app
turns these values into labels such as `Revisar` or `Sin CIP`, allowing a user
or maintainer to check the original notice.
