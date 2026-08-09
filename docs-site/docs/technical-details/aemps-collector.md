# Spain (AEMPS) Collector

The Spain collector first asks the public AEMPS search service for pages that
might be medicine recalls. These possible matches are called candidates. It
then opens each candidate and rejects pages that are not relevant.

The search endpoint is:

```text
https://www.aemps.gob.es/wp-json/aemps-search/v1/search
```

## Finding Candidates

The collector uses several Spanish search phrases, including `Nº alerta`,
`Retirada medicamento lote`, and `defecto calidad medicamento`. Full builds add
the year to these searches and move through every result page with `page=N`.

Search results can include unrelated material. The collector removes obvious
veterinary, cosmetic, product-safety, and general news pages before and after
reading the detail page.

An accepted human-medicine alert normally has an identifier such as:

```text
R_21/2026
```

Veterinary identifiers such as `VDC` are rejected.

## Reading a Notice

AEMPS detail pages normally provide labeled fields such as:

- `Nº alerta`
- `Fecha`
- `Producto`
- `Marca comercial y presentación`
- `Lote`
- `Laboratorio titular`
- `Clasificación de los defectos`
- `Descripción del defecto`

HTML is the first choice because it is faster to download and easier to parse.
If required fields are missing and AEMPS links a PDF, the collector can inspect
that PDF with `pdfplumber`. The PDF is stored only in temporary space and is not
committed to the repository.

## Maintenance Risk

AEMPS can change page templates, labels, and search behavior. When a real page
introduces a new format, add a small fixture that reproduces it and update the
adapter test before broadening the parser.
