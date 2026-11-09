# CIMT HS6 Imports: Initial Verified Discovery (2020–2025)

Original files: `data/source_exports/cimt/2202.10.csv`, `2202.91.csv`, `2202.99.csv`, uploaded unchanged from the [Statistics Canada CIMT Web Application](https://www150.statcan.gc.ca/n1/pub/71-607-x/71-607-x2021004-eng.htm); source files include "Accessed date: 2026-11-09".

## Data quality and provenance
- **Imports only**, Canada total as reporting geography, 2020-01 to 2025-12, HS6 commodity codes, all trading partners (countries and states of the United States).
- All three files contain **72 distinct calendar months** and nonnegative numeric value/quantity.
- **15,670 authentic source observations:** 2202.10 = **7,577**; 2202.91 = **1,533**; 2202.99 = **6,560**.
- Duplicate source-grain observations **0**. Missing value / quantity **0**. Original unit **Volume in litres** for all rows; `Value ($)` as reported in **Canadian dollars**.
- **Do not discard US state records:** the source splits US-origin goods into numerous states including an "Unknown states" category. Aggregated US import amount is calculated as the sum of those distinct state observations; original state is preserved in the normalization pipeline.
- **Country = Canada** is a source partner value found on imports; **it is not a World/Canada total** and must not be used as the denominator for a partner-share calculation.
- The raw files include a one-line "Imports" title before the actual CSV header and trailing attribution lines; the ETL discards the wrapper/footer but **not source data**.
- Git blob SHAs: 2202.10 `df85796fa5b775bf4dfb5a0c2a6840ab00b9590e`; 2202.91 `55523138c7c15e49f7f61c8e7c7e639a82cd5b5d`; 2202.99 `bb364fb851097fe78d9291588733a36c7c219167`.

## Product scope
| HS6 | Category | Role |
|---|---|---|
| 220210 | Waters, including sweetened/flavoured | Core soft-drink trade |
| 220291 | Non-alcoholic beer | Separate optional segment |
| 220299 | Other non-alcoholic beverages excluding non-alcoholic beer and HS 2009 juice | Core other-beverages trade |

Descriptions are source-period-specific and may change wording across HS vintages. The exact HS6 classification concordance for 2020–2025 should still be reviewed before attributing longitudinal changes solely to demand.

## Value of selected imports (CAD millions, nominal, calculated by summing source rows)

| Year | HS 220210 | HS 220291 | HS 220299 |
|---|---:|---:|---:|
| 2020 | 443.052 | 20.977 | 753.157 |
| 2021 | 482.792 | 23.925 | 691.553 |
| 2022 | 612.609 | 23.395 | 671.913 |
| 2023 | 693.875 | 29.935 | 746.476 |
| 2024 | 759.856 | 41.644 | 752.963 |
| 2025 | 742.468 | 36.749 | 917.338 |

These numbers represent **only the selected HS headings**, not total non-alcoholic beverage imports; they exclude HS 2201 and HS 2009, among others. This dataset cannot establish market share of retail purchases or trade balance because it contains imports only.

## Ready-to-chart outputs
- `data/curated/cimt_imports_monthly_totals_2020_2025.csv`: 216 month × HS observations, 72 per code.
- `data/curated/cimt_imports_annual_totals_2020_2025.csv`: 18 year × HS observations.
- `data/curated/cimt_imports_annual_partner_2020_2025.csv`: year × HS × partner, US states aggregated correctly to United States.
- `etl/prepare_cimt_exports.py`: reproducibly creates full normalized 15,670-observation data and detailed country-month aggregates locally, with US state retained.
- `powerbi/cimt_imports_from_github.pq`: reads original three files directly in Power BI Desktop and retains partner state in each observation.

The derived data are strictly for analytics and can be recreated from the originals; do not alter the source files.

## Verified MySQL 8 integration run (2026-11-09)

[GitHub Actions CIMT integration](https://github.com/Ethannguye/canadian-beverage-market-analytics/actions/runs/42571409692) **PASSED**. The workflow:
- parsed three original files into **15,670** record-level observations;
- created **9,898** source country × month × HS groups and **216** month × HS totals;
- loaded all **15,670** records to a **temporary GitHub Actions MySQL 8 test database**, preserving partner states;
- confirmed source row count and each HS6 **2025 import total** exactly (all checks printed PASS);
- uploaded normalized CSV, partner-month CSV and profile as a temporary build artifact.

**This does not populate the user's local MySQL database and does not mean a Power BI .pbix has been created.** The normalized file can be reproduced with `python etl/prepare_cimt_exports.py`. Product codes remain in `candidate` review status in the fact database until the classification source audit.
