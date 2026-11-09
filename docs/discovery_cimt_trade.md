# Verified Canada HS6 imports and total exports: 2020–2025

**Official source:** [Statistics Canada CIMT Web Application](https://www150.statcan.gc.ca/n1/pub/71-607-x/71-607-x2021004-eng.htm).

Six user-downloaded original CSVs were checked at `data/source_exports/cimt/`, with source citation footer "Accessed date: 2026-11-09". The import files have `Imports` as the first line, the export files have **`Total exports`**, which includes domestic exports and re-exports. Neither set is automatically equivalent to domestic production.

## Six source files and audit

| HS6 | Imports file | Import records | Total exports file | Export records |
|---|---|---:|---|---:|
| 220210 | `2202.10.csv` | 7,577 | `E2202.10.csv` | 3,695 |
| 220291 | `2202.91.csv` | 1,533 | `E2202.91.csv` | 976 |
| 220299 | `2202.99.csv` | 6,560 | `E2202.99.csv` | 4,293 |
| **Total** | | **15,670** | | **8,964** |

All six have 72 distinct months from January 2020 to December 2025; numeric CAD values and litre quantities are nonnegative, no missing required fields, and zero duplicate observations at the source grain (flow × month × HS6 × country × state × reporting geography × unit).

**Export source Git blob SHAs:** `E2202.10.csv`: `8c8a21fe571bc5247d2c48d224e17604bc958265`; `E2202.91.csv`: `278f70f3a42c77461eaa6fc0b4b77191a5d2c3e0`; `E2202.99.csv`: `86914406a5a05c536d8f46ddf58c577a719e29c2`.

## Sum of selected three codes: annual trade balance

CAD millions (nominal), derived exclusively from source values:

| Year | Imports | Total exports | Trade balance (exports − imports) |
|---|---:|---:|---:|
| 2020 | 1,217.186 | 464.220 | -752.967 |
| 2021 | 1,198.271 | 494.750 | -703.521 |
| 2022 | 1,307.916 | 577.842 | -730.074 |
| 2023 | 1,470.286 | 721.647 | -748.639 |
| 2024 | 1,554.463 | 788.208 | -766.255 |
| 2025 | 1,696.555 | 782.798 | -913.757 |

**Scope warning:** These are only HS6 `220210` (sweetened or flavoured waters), `220291` (non-alcoholic beer) and `220299` (other non-alcoholic beverages). They **exclude** unsweetened water under HS2201 and fruit/nut/vegetable juice under HS2009, and they are **not a complete balance for the Canadian beverage industry**. Distinct product categories must not be conflated with the retail revenue dataset.

## Data engineering outputs

- `etl/prepare_cimt_trade.py`: validates all six original files, retains the US state detail at record grain, combines imports and total exports and writes derived data to `data/processed/`.
- `data/curated/cimt_trade_monthly_balances_2020_2025.csv`: 216 monthly HS6 rows.
- `data/curated/cimt_trade_annual_balances_2020_2025.csv`: 18 annual HS6 rows.
- `data/curated/cimt_trade_annual_partner_2020_2025.csv`: 1,656 year × HS × partner-country rows; original US states summed once to United States at the partner level.
- `powerbi/cimt_trade_from_github.pq`: dynamically reads the six source files for Power BI Desktop, including US state and trade flow.
- `sql/04_analytical_views.sql`: approved-only monthly HS trade balance view.
- `.github/workflows/cimt-integration.yml`: integration tests on a *temporary* MySQL 8 database; **not** a deployment to the user's local database.

### Accuracy notes

- Partner country `Canada` in import files is original data and not a World total.
- The U.S. is reported at state level in original files; do not mistakenly mix U.S. states with a U.S. country subtotal.
- Month and year aggregates use sum of original dollars and litres, without currency, inflation or volume adjustments.
- Values may be revised by Statistics Canada on later downloads; always preserve original filename and accessed date.
- The exact HS vintage classification and market-enterprise opportunity interpretation still require careful source review.

## Verified end-to-end MySQL 8 integration (2026-11-09)

[Import + Total Export MySQL CI workflow](https://github.com/Ethannguye/canadian-beverage-market-analytics/actions/runs/42573045003) **PASSED**. It normalized all six original CSVs and loaded **24,634** rows in a **temporary GitHub Actions MySQL 8 database**, preserving trade flow and U.S. state. The workflow validated each HS6's 2025 import amount, total export amount, and monthly SQL trade balance, and uploaded temporary normalized-data artifacts. It does not update the user's local MySQL instance.

[Regression tests](https://github.com/Ethannguye/canadian-beverage-market-analytics/actions/runs/42573458762) **PASSED**, including exact re-creation of every committed annual, monthly and country-level aggregate from the six source CSVs.
