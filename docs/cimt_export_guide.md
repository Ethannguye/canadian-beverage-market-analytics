# CIMT export guide — partner × HS product data

Official application: https://www150.statcan.gc.ca/n1/en/catalogue/71-607-X2021004

This workstream requires an **authentic export** or another explicitly licensed verified trade dataset. The project does not contain invented trade data and does not scrape the application.

## Selection checklist
1. Select monthly data for 2020-01 through 2025-12; use customs-based values consistently.
2. Product scope: first examine headings 2009, 2201 and 2202, and if necessary use homogeneous six-digit subheadings. Confirm descriptions for each vintage.
3. Trade flow: Imports and Exports must be separate.
4. Partner: capture trading partner as published; avoid mixing a 'World' aggregate with individual partners when summing.
5. Geography: collect a **Canada** total; provincial customs clearance may be used in a separate view but does not represent final consumer demand.
6. Measures: record value in **Canadian dollars**, plus quantity and its original unit only if reported.
7. Keep the original export and a note of extraction date, source, filters, and selected classification.

## Normalized CSV interface
Copy the header-only template `data/exports/cimt_normalized_template.csv` to a working CSV and populate with rows taken from the verified source.
```csv
reference_period,hs_code,commodity_name,trade_flow,partner_country,partner_state,clearance_geography,value_cad,quantity,quantity_unit,source_note,classification_version
```
- `reference_period`: YYYY-MM.
- `hs_code`: 4–10 digits under 2009 / 2201 / 2202.
- `trade_flow`: Import or Export.
- `partner_country`: verbatim source partner (not inferred).
- `partner_state`: preserve original State (for US subdivisions); use `N/A` otherwise. Never collapse US states into one row without aggregating values.
- `clearance_geography`: e.g., Canada or exact source province label.
- `value_cad`: numeric CAD amount. Do not use a 'thousands of dollars' number without explicitly multiplying by 1000 and documenting conversion.
- `quantity`: optional numeric quantity; `quantity_unit` blank when quantity blank.
- `source_note`: identify official export, date and filters.
- `classification_version`: exact HS vintage when known or `source-vintage-unverified` if not.

## Import after reviewing the source
```bash
python etl/load_cimt_csv.py data/exports/cimt_normalized_2020_2025.csv
```
The importer enforces schema, dates, numeric fields and duplicate grains, but it **cannot verify source authenticity**. Newly encountered products remain `candidate` until an analyst validates and approves the HS classification.
