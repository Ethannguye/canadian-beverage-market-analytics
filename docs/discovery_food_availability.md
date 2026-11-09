# Initial official-source discovery: Table 32-10-0054-01

- **Downloaded:** 2026-11-09T05:18:02Z, StatCan WDS
- **Full ZIP sha256:** `eb6c1703529c6e47854b5df1ef3fa84d9a006841af1adde86848f2bdcade29a4`
- **Original source:** [Statistics Canada Food available in Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210005401)
- **GitHub Actions evidence:** [successful discovery run](https://github.com/Ethannguye/canadian-beverage-market-analytics/actions/runs/42566469263)
- **Source full table:** 35,143 rows across all published periods/food categories.
- **Initial regex-selected candidates (2020–2025):** 84 rows; 8 labels, 20 missing values.
- **Curation:** The narrower 24-row `data/curated/food_availability_2020_2025.csv` has only base series (**Food available**, not **adjusted for losses**) and 4 non-alcoholic beverage labels; source vector IDs preserved.
- **Excluded:** Ciders/coolers (outside the strict non-alcoholic scope); loss-adjusted duplicate series; weight-equivalent tea/coffee series so that litre figures remain comparable by unit.
- **Important:** Bottled-water observations are missing in every year for this series; year 2024 is missing for the three usable liquid beverage series. Missing is not zero.
- **Units:** Litres per person per year, *availability*, not recorded retail purchases or individual drinking behavior.

## First observed end-point changes, 2020 vs 2025
| Commodity | 2020 | 2025 | Change | Source vector |
|---|---:|---:|---:|---|
| Soft drinks | 52.72 | 42.53 | -19.33% | v108443 |
| Coffee | 105.04 | 97.74 | -6.95% | v783724 |
| Tea | 77.74 | 94.70 | +21.82% | v783723 |
| Bottled water | unavailable | unavailable | not calculable | v783736 |

All values are as published and in litres per person per year. Percent changes are calculations from the two observations, **not** compound annual growth estimates; the unobserved 2024 interval cannot be inferred. Do not label availability as actual consumption.

## Data-quality caveats
- The broad regex also found cider/cooler series; a preliminary alcohol exclusion was added to the ETL. An analyst must still approve exact metadata-coded products.
- The table contains both `Food available` and `Food available adjusted for losses`; mixing or summing them would double count.
- Never infer bottled-water growth from this table. Look for other official sources if bottled-water analysis is required.
