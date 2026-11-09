# Canadian Non-Alcoholic Beverage Market Analytics (2020–2025)

A reproducible portfolio project studying **Canada's domestic non-alcoholic beverage market and international trade** using public Canadian statistics, Python, MySQL, and Power BI.

> **Project status (2026-11-09):** Six authentic CIMT HS6 files now checked: **15,670 imports + 8,964 total-export records = 24,634** for 2020–2025, alongside 672 domestic-market observations. Reproducible transformation scripts, QA, MySQL 8 CI and Power Query links are in the repository. HS2201/HS2009, final local MySQL data deployment and the six-page PBIX remain pending.

## Research questions
1. How did relevant retail-product sales change during 2020–2025?
2. How did beverage consumer prices and per-capita availability change?
3. How did Canadian merchandise trade in selected beverage commodities change?
4. Which commodity categories and trade partners warrant further market-entry research?
5. What are the limitations of using official aggregate data for business decisions?

## Data sources
| Workstream | StatCan table / application | Frequency | Caveat |
|---|---|---|---|
| Retail (2020–2022) | [20-10-0017-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010001701) | Monthly | NAPCS 2017, archived; not automatically comparable with post-2022 |
| Retail (2023–2025) | [20-10-0080-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010008001) | Monthly | NAPCS 2022 |
| Consumer price index | [18-10-0004-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401) | Monthly | Index, not retail price dollars |
| Food availability | [32-10-0054-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210005401) | Annual | Supply availability, not observed consumption |
| Manufacturing | [16-10-0048-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1610004801) | Monthly | Verify industry codes & units before interpretation |
| Industry merchandise trade | [12-10-0176-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017601) | Monthly | Industry-level, *not* HS or individual partner by default |
| HS commodity & partner trade | [CIMT](https://www150.statcan.gc.ca/n1/en/catalogue/71-607-X2021004) | Monthly | Export verified HS 2009/2201/2202 data separately; no invented market shares |

The [Statistics Canada Web Data Service](https://www.statcan.gc.ca/en/developers/wds/user-guide) can return full-table CSV downloads. Each export can be revised; reruns log the acquisition timestamp and source.

## Architecture
```
Statistics Canada / verified CIMT CSV exports
                |
    etl/download_statcan.py
                |
   data/raw/ (ignored by Git)
                |
      etl/prepare_statcan.py
                |
   data/processed/ (CSV staging)
                |
    MySQL source staging + fact tables
                |
         Power BI report
```

## Getting started
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python etl/download_statcan.py --tables 32100054
python etl/prepare_statcan.py --tables 32100054
python -m unittest discover -s tests -v
```
**Note:** Full-table exports can be very large. Start with one table, check its metadata, dimensions, and product codes, and only then expand. The project currently does **not** bundle a ready-to-run PBIX or comprehensive market-wide totals. Published import sums are strictly for the selected HS6 codes.

## Ready-to-use verified data

| Dataset | Rows | File |
|---|---:|---|
| Retail two leaf categories | 144 | [CSV](data/curated/retail_beverage_2020_2025.csv) |
| CPI (Canada/Ontario and beverage categories) | 360 | [CSV](data/curated/cpi_beverages_2020_2025.csv) |
| Food available per person | 24 | [CSV](data/curated/food_availability_2020_2025.csv) |
| Manufacturing shipments, Ontario/Quebec | 144 | [CSV](data/curated/manufacturing_soft_drinks_2020_2025.csv) |
| CIMT raw imports and total exports HS220210/220291/220299 | 24,634 | [six original files](data/source_exports/cimt/) |
| CIMT monthly HS6 aggregates | 216 | [CSV](data/curated/cimt_imports_monthly_totals_2020_2025.csv) |
| CIMT yearly partner aggregates (imports only) | 1,398 | [CSV](data/curated/cimt_imports_annual_partner_2020_2025.csv) |
| CIMT annual import/export trade balances | 18 | [CSV](data/curated/cimt_trade_annual_balances_2020_2025.csv) |
| CIMT monthly import/export trade balances | 216 | [CSV](data/curated/cimt_trade_monthly_balances_2020_2025.csv) |

**Power BI quick start:** [import domestic indicators and both HS6 trade flows using ready-made Power Query scripts](powerbi/QUICKSTART_CSV.md). Core category/method limits remain described under `docs/`.

## Reproduce partner-level imports

```bash
python etl/prepare_cimt_exports.py
# Outputs include data/processed/cimt_imports_normalized_2020_2025.csv
# Requires MySQL 8+ schema and credentials for the next step:
# python etl/prepare_cimt_trade.py
# python etl/load_cimt_csv.py data/processed/cimt_trade_normalized_2020_2025.csv
```

**Trade-balance source audit:** [see six-file verification and calculations](docs/discovery_cimt_trade.md).

## Planned deliverables
- Data acquisition logs, source inventory and data dictionary
- Cleaned, reproducible 2020–2025 data (where available)
- Tested MySQL schema and data-quality SQL
- Six-page Power BI specification, DAX measures and final report
- Explicit classification reconciliation, limits, source attribution

## Data integrity rules
- Keep raw source classifications and separate fact-table grains.
- Never sum CPI, availability, retail sales, and imports into a synthetic 'market size'.
- Treat **province of clearance** as customs clearance location, not consumption.
- Record the 2023 NAPCS break; only compare matched categories.
- Do not calculate country market shares from an industry-by-all-countries total. For CIMT, sum US state observations to US country totals and never mistake partner Country=Canada for a World subtotal.
- No simulated market figures presented as real results.

## License
Code: MIT license. Statistics Canada and other third-party data retain their own terms and attribution requirements.
