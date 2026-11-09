# Soft drink and ice manufacturing — 16-10-0048-01

Source: [Statistics Canada Manufacturing sales by industry and province, monthly](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1610004801).
GitHub Actions [source discovery run](https://github.com/Ethannguye/canadian-beverage-market-analytics/actions/runs/42567230279).

- Full table downloaded and parsed: **1,292,995 rows**.
- Initial regex discovery: **3,312 candidate rows**; **1,985 missing/suppressed** values among broad beverage/manufacturing categories and province combinations.
- Selected published series: industry **Soft drink and ice manufacturing [31211]**, measure **Sales of goods manufactured (shipments)**, **Unadjusted**; Ontario vector **v805716**, Québec vector **v805256**.
- These two provincial series have **72 monthly observations each**, 2020-01–2025-12, with no missing numeric values in this selected pair (**144 rows**).
- Published unit: **thousands of Canadian dollars**; the original scalar factor is `thousands`.
- Published industry includes **ice**; it is not purely bottled drinks. **Manufacturing shipments are not retail revenues or beverage consumption**.
- NAICS 2022 changes and source revisions can affect historical comparisons; retain the original code and audit context.

## Published summed monthly values (millions CAD; nominal)
| Year | Ontario | Québec |
|---|---:|---:|
| 2020 | 1,609.409 | 790.437 |
| 2021 | 2,011.105 | 1,054.819 |
| 2022 | 2,404.383 | 1,126.084 |
| 2023 | 2,375.452 | 1,220.439 |
| 2024 | 2,559.623 | 1,378.253 |
| 2025 | 2,454.217 | 1,451.334 |

Do not add broad parent NAICS 312 or 3121 to NAICS 31211 as they overlap. These two provinces are an illustration, **not a total for Canada**.
