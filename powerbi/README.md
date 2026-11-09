# Power BI report implementation guide

**Status:** Five Power Query connectors for real curated domestic-source and authentic HS6 import data are ready. A ready-to-open .pbix is **not yet available**.
Power BI Desktop is normally run on Windows. The user can open this repo on a school Windows PC or another machine running Power BI Desktop.

## Quick import (no MySQL required)

See [QUICKSTART_CSV.md](QUICKSTART_CSV.md). The `cimt_imports_from_github.pq` Power Query reads the three original user-exported Statistics Canada import files; it skips the first title row and source citation footer, retains `PartnerState`, and filters 2020–2025. The other four .pq files read verified domestic indicators.

## Import data
Home > Get data > MySQL database. Server: localhost (if MySQL is on the same Windows machine). Database: canadian_beverage_market. Select Import mode for a small 2020–2025 curated model.
Select the reviewed SQL views:
- vw_retail_approved
- vw_cpi_approved
- vw_availability_approved
- vw_manufacturing_approved
- vw_trade_industry_approved
- vw_hs_trade
- vw_hs_import_partner_canada

Alternatively, export view data to CSV from MySQL Workbench if the Windows PC cannot access the MySQL server. Do not connect to the developer's Mac localhost from Windows; 'localhost' always means the machine running Desktop.

## Six report pages
1. Executive Overview — cards; cross-source trends only with separate axes/units.
2. Domestic Retail — monthly published values; NAPCS vintage slicer; do not bridge 2022–2023 blindly.
3. Imports (Exports pending) — actual HS220210/220291/220299 values by month, product and partner; preserve US states. No trade balance until exports are collected.
4. Pricing & Availability — CPI YoY as rate; annual food availability in a separate visual.
5. Manufacturing & Regional — source-compliant province/industry breakdown.
6. Market Entry Opportunities — partner concentration, growth and a **transparent illustrative** opportunity scoring rubric.

## Modelling notes
- Build a Date table with one row per day and mark as Date table.
- Convert YYYY-MM `reference_period` strings to first-of-month Date columns in Power Query, and annual years separately.
- Relationships are per source; never create circular fact-to-fact joins.
- Keep units and classification vintage visible as slicers/tooltips.
- Use only **reviewed** views. An empty chart is expected until source approvals and loading.
- Before reporting any metric, cross-check Power BI numbers with SQL totals for exactly the same grain and filters.
- Do not sum CPI; use an index level, calculate YoY percentages.
- Never aggregate both HS heading and its child subheadings, or both 'World' and underlying countries. **Source partner Country=Canada is not a World total.**

See `powerbi/measures.dax` for copyable DAX examples after adapting the table and field names.
