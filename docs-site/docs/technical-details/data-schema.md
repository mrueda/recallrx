# Data Schema

Records are country-scoped so multiple authority sources can coexist without id
collisions.

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

## Field groups

<div className="schemaGrid">
  <div className="schemaPill"><strong>Identity</strong>country, authority, id, local_id</div>
  <div className="schemaPill"><strong>Product</strong>medicine, manufacturer, product_codes, lots</div>
  <div className="schemaPill"><strong>Evidence</strong>source_url, pdf_url, confidence, warnings</div>
</div>

## Product codes

Product codes keep their source-specific system:

```json
{"system": "CN", "value": "755215"}
```

Current examples include Spain `CN`, Portugal `AIM`, and France `CIP`. Future
adapters should use their national product code systems without changing the
field shape.

## Confidence and warnings

`confidence` is a parser confidence score, not a clinical or regulatory risk
score. `warnings` record missing or fallback-extracted fields so reviewers can
inspect imperfect records.
