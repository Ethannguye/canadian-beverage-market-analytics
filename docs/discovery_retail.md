# Initial retail discovery: verified monthly beverage series

**Official sources:** [20-10-0017-01 (NAPCS 2017)](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010001701) and [20-10-0080-01 (NAPCS 2022)](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010008001). Official WDS original extracts obtained via successful [2026-11-09 workflow](https://github.com/Ethannguye/canadian-beverage-market-analytics/actions/runs/42566804867) for **retail only**. The combined workflow's industry-trade job exceeded the intentionally enforced 600 MB download limit; that is a pending workstream, not missing retail data.

## Scope and basis
- 2020–2022: code **5611211**, vector **v1059484393** (soft drinks excluding bottled water), code **5611212**, vector **v1059484394** (other non-alcoholic beverages except soft drinks, milk, hot/frozen drinks).
- 2023–2025: code **5611141**, vector **v1456717018**; code **5611142**, vector **v1456717019** (similar labels under **NAPCS 2022**).
- Exactly **144 monthly source observations**, 36 months per original series; **no missing values** in these selected series.
- Original unit: **Dollars with scalar factor thousands**; CSV column `value_cad_thousands` preserves the published values (value 232529 = 232.529 million CAD).
- The two selected categories are leaf labels; no combined parent/child category totals, alcoholic, cannabis, or hot-prepared beverages.

## Source-verified annual totals (millions of CAD; sum of monthly published current-dollar sales)

| Year | Soft drinks (except bottled water) | Other non-alcoholic beverages | Vintage |
|---|---:|---:|---|
| 2020 | 3,367.939 | 5,604.642 | NAPCS 2017 |
| 2021 | 3,575.642 | 6,135.570 | NAPCS 2017 |
| 2022 | 4,117.059 | 6,757.304 | NAPCS 2017 |
| 2023 | 4,540.377 | 7,391.635 | NAPCS 2022 |
| 2024 | 4,660.670 | 7,954.009 | NAPCS 2022 |
| 2025 | 4,883.636 | 8,102.090 | NAPCS 2022 |

**CRITICAL:** Source categories changed classification and Retail Commodity Survey scope from January 2023. **Do not calculate uninterrupted 2020–2025 CAGR or 2022→2023 YoY** unless a proven concordance and scope comparability audit has been completed. Show distinct groups/markers in Power BI. 2023→2025 within the newer vintage is safer, subject to revisions.

Retail revenue is not the whole Canadian beverage market: categories cover retail sales represented in the survey; foodservice, direct sales and wholesale may differ. Figures are nominal and should be analyzed alongside CPI, not labeled real growth.

Data selection is auditable by PID and VECTOR; the snapshot was normalized from official exports and stored in `data/curated/retail_beverage_2020_2025.csv`.
