# CPI source discovery and series curation — 18-10-0004-01

Original official data: [Statistics Canada monthly CPI](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401).
Pipeline run: [Successful CPI + manufacturing acquisition](https://github.com/Ethannguye/canadian-beverage-market-analytics/actions/runs/42567230279).

The full official cube had **1,154,918 rows**. The candidate regex yielded **8,069 observations** across 14 category labels (including unwanted alcoholic and composite categories). Only five precise non-alcoholic category/geography vectors were kept in `data/curated/cpi_beverages_2020_2025.csv`:
- Canada, Non-alcoholic beverages — v41691045
- Ontario, Non-alcoholic beverages — v41691950
- Canada, Fruit juices — v41691017
- Canada, Coffee — v41691037
- Canada, Tea — v41691038

Each vector has **72 monthly observations**, 2020-01–2025-12; **360 rows**, no missing values. Unit/index base is **2002=100**. This index is **not** a retail price per bottle or a dollar amount. **Never SUM index levels across time/categories**. To calculate YoY, compare the same original CPI series to the same month one year earlier.

Other category labels such as 'All-items excluding alcoholic beverages...' are index aggregates and were excluded. Sources and original vectors are preserved for auditing.
