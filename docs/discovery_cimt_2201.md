# HS 2201 unsweetened waters / ice and snow: complete trade audit

Four authentic original Canada CIMT CSV files were uploaded on **2026-11-09**, and the two export files were **replaced with complete versions** after the first exports were missing October–December 2025.

Official source: [Statistics Canada CIMT](https://www150.statcan.gc.ca/n1/pub/71-607-x/71-607-x2021004-eng.htm), accessed 2026-11-09.

## Source file validation

| File | Trade direction | Verified source rows | Distinct months | Original Git blob SHA |
|---|---|---:|---:|---|
| `I2201.10.csv` | Imports | 4,330 | 72/72 | `723a7a9d38abf7b8effe6f64920189f51baa4c8d` |
| `I2201.90.csv` | Imports | 4,816 | 72/72 | `34e5f9bdc4517f6dc95105d341841728d22dc718` |
| `E2201.10.csv` | Total exports | 1,253 | 72/72 | `aa0384caedefc9303cd38621dc62be689692c29d` |
| `E2201.90.csv` | Total exports | 1,164 | 72/72 | `24e8f73c47122b53a29f1bb901bce0c28342c100` |
| **Total** | | **11,563** | | |

The four files preserve the exact source fields `Period, Commodity, Province, Country, State, Value ($), Quantity, Unit of measure`. The import source labels use `2201.10` and `2201.90`, while the export labels use `2201.10.00` and `2201.90.00`. These are normalized to common **HS6 codes 220110 and 220190** without modifying the original product descriptions.

The inputs have no duplicate month × flow × code × partner × US state × geography rows, no missing mandatory numeric fields, no negative amounts, and the original quantity unit is `Volume in litres`.

## Trade values by year and HS6

Unit **million CAD**, nominal, from exactly the uploaded source rows. Balance = Total exports − Imports.

| Year | HS6 | Imports | Total exports | Balance |
|---|---|---:|---:|---:|
| 2020 | 220110 | 81.693 | 14.321 | -67.372 |
| 2020 | 220190 | 28.400 | 13.270 | -15.130 |
| 2021 | 220110 | 81.570 | 15.222 | -66.348 |
| 2021 | 220190 | 32.020 | 15.337 | -16.683 |
| 2022 | 220110 | 100.345 | 10.972 | -89.373 |
| 2022 | 220190 | 35.559 | 32.467 | -3.093 |
| 2023 | 220110 | 109.276 | 14.300 | -94.975 |
| 2023 | 220190 | 38.293 | 22.517 | -15.776 |
| 2024 | 220110 | 87.688 | 17.283 | -70.405 |
| 2024 | 220190 | 40.851 | 14.059 | -26.793 |
| 2025 | 220110 | 98.741 | 11.315 | -87.426 |
| 2025 | 220190 | 49.177 | 15.556 | -33.621 |

The 2025 selected HS 2201 combined balance is **−121.047 million CAD**. Combined with the three HS 2202 codes already curated, the 2025 balance of the **five selected HS6 categories** is **−1,034.804 million CAD**. This is **not** an industry-wide trade deficit.

## Classification and business-interpretation caveats

- **HS 220110**: Mineral and aerated waters without added sweeteners or flavouring.
- **HS 220190**: Other potable waters **plus ice and snow**. **Do not label the full value as bottled water revenue**. The HS6 code alone cannot isolate all packaged water from ice/snow; the separation requires more detailed commodity classification.
- **Exports are "Total exports"** and may include re-exports, not just domestically manufactured beverages.
- The source reports the Canadian reporting geography and country or US-state trade partners, **not retail purchases or brand-level sales**.
- Source partner `Canada` is not a World total. Do not add a heading to its subheading totals or count individual US states in addition to an already aggregated US country figure.
- The source HS vintage definitions and annual revisions need review before interpreting growth as changes in demand.

## Reproducible outputs

- `etl/prepare_cimt_2201.py`: independently parses the four original files.
- `etl/prepare_cimt_all.py`: rebuilds the HS 2201 and HS 2202 slices and combines all ten original files.
- `data/curated/cimt_2201_trade_monthly_balances_2020_2025.csv`: **144** monthly records.
- `data/curated/cimt_2201_trade_annual_balances_2020_2025.csv`: **12** year × HS records.
- `data/curated/cimt_2201_trade_annual_partner_2020_2025.csv`: **1,004** year × HS × country records.
- `data/curated/cimt_all_trade_monthly_balances_2020_2025.csv`: **360** month × HS records.
- `data/curated/cimt_all_trade_annual_balances_2020_2025.csv`: **30** year × HS records.
- `data/curated/cimt_all_trade_annual_partner_2020_2025.csv`: **2,660** year × HS × country records.

Do not treat the `data/curated/` summaries as the full record-level database; the normalized 36,197-row output is generated under `data/processed/` and is available as a GitHub Actions artifact.
