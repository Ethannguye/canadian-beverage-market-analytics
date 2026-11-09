# Canadian Non-Alcoholic Beverage Market Analytics (2020–2025)

A reproducible portfolio project studying **Canada's domestic non-alcoholic beverage market and international trade** using public Canadian statistics, Python, MySQL, and Power BI.

> **Project status (2026-11-09):** Data-source inventory and engineering foundation started. **No market figures or dashboards are claimed as completed.** Raw data must be downloaded, validated, and modeled before drawing conclusions.

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
**Note:** Full-table exports can be very large. Start with one table, check its metadata, dimensions, and product codes, and only then expand. The project currently does **not** bundle a ready-to-run PBIX or verified market totals.

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
- Do not calculate country market shares from an industry-by-all-countries total.
- No simulated market figures presented as real results.

## License
Code: MIT license. Statistics Canada and other third-party data retain their own terms and attribution requirements.
