# AEMPS Collector

The Spain adapter discovers candidate posts through the public AEMPS search
endpoint:

```text
https://www.aemps.gob.es/wp-json/aemps-search/v1/search
```

It uses query variants such as `Nº alerta`, pages through results with
`page=N`, and filters candidates after parsing.

## Filtering

The MVP accepts human-medicine recall ids like:

```text
R_21/2026
```

It rejects veterinary alerts such as `VDC`, cosmetics, product-safety notices,
and general AEMPS news posts.

## Parsing strategy

The parser uses AEMPS HTML as the primary source because current recall detail
pages expose labels such as:

- `Nº alerta`
- `Fecha`
- `Producto`
- `Marca comercial y presentación`
- `Lote`
- `Laboratorio titular`
- `Clasificación de los defectos`
- `Descripción del defecto`

When HTML misses required fields, the adapter may download the linked PDF to
temporary storage and inspect it with `pdfplumber`. PDFs are not committed.

## Known risks

AEMPS page templates and labels can change. Keep parser fixtures compact and
add new label variants only when real pages require them.
