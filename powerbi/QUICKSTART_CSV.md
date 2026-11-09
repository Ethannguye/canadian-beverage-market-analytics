# Power BI Desktop: start with authentic data immediately

The repository currently includes four **real, checked domestic-market CSVs**, plus ten official CIMT HS6 import and total-export CSVs:
- `data/curated/retail_beverage_2020_2025.csv` — 144 monthly observations, two distinct non-overlapping NAPCS retail leaf categories.
- `data/curated/food_availability_2020_2025.csv` — 24 annual availability observations including explicit missing values.
- `data/curated/cpi_beverages_2020_2025.csv` — 360 CPI observations, five distinct series (Canada and Ontario).
- `data/curated/manufacturing_soft_drinks_2020_2025.csv` — 144 monthly shipment observations for Ontario and Quebec.

No MySQL setup is required to preview these datasets in Power BI. The CIMT files can be connected via a fifth Power Query.

## Steps in Windows
1. Open Power BI Desktop > **Home > Transform data > Power Query Editor**.
2. **New Source > Blank Query > Advanced Editor**. Paste contents of `powerbi/retail_from_github.pq`. Rename query `RetailBeverages`.
3. Add another Blank Query. Paste `powerbi/availability_from_github.pq`. Rename query `FoodAvailability`.
4. Repeat with `powerbi/cpi_from_github.pq` (rename `BeverageCPI`) and `powerbi/manufacturing_from_github.pq` (rename `Manufacturing`) to get all four curated datasets.
5. Add a Blank Query and paste `powerbi/cimt_trade_from_github.pq`. Rename it **`CIMTTrade`**. This reads all **10 original files** (Imports + Total exports) and preserves US state data. **Do not also load the older `CIMTImports` query**, or import totals will be duplicated.
6. Select **Close & Apply**. For public source credentials choose **Anonymous**.
7. On report page **Domestic Retail**, choose a clustered column chart: Axis `year`; Legend `product_group`; Values SUM(`sales_cad_millions`). Add a **classification_vintage** slicer and visibly mark the 2023 break.
8. On page **Food Availability**, choose a line chart: X Axis `year`; Y Axis `value`; Legend `product`; add a filter `value_status = observed`. The 2024 gap must remain blank; bottled-water series has no observed values.
9. Save as `powerbi/Beverage_Market_Analytics.pbix` on your Windows PC; large PBIX files are intentionally excluded from Git until reviewed.

## Validation
- CIMT: 36,197 observations (24,816 Imports + 11,381 Total exports), across five HS6 codes, 72 months per flow and code; state-level US rows are not country-level subtotals.
- CIMT 2201 values in 2025: 220110 Imports **98,740,904 CAD**, Total exports **11,315,171 CAD**; 220190 Imports **49,177,038 CAD**, Total exports **15,555,617 CAD**. Note HS220190 includes ice and snow.
- CIMT value 2025: 220210 = **742,467,960 CAD**; 220291 = **36,748,545 CAD**; 220299 = **917,338,369 CAD**. Calculate with the `CIMT Imports CAD` / `CIMT Total Exports CAD` measures on `CIMTTrade`, filtered to a specific HS and Year.

- Retail has **144** rows (4 published source series × 36 months) and two categories each year.
- Unit is CAD **millions** in the M query, converted from published **thousands of CAD** by dividing by 1000.
- 2023 soft-drink annual sum = **4,540.377 million CAD**; 2025 = **4,883.636 million CAD**. Compare precisely matching filters.
- 2024 per-person availability is unavailable for the current 3 usable liquid series, **not zero**.

## Trade-balance visual

- Create measures from `powerbi/cimt_trade_measures.dax` using the `CIMTTrade` table.
- Plot `Year` on the horizontal axis and the **CIMT Imports CAD**, **CIMT Total Exports CAD** and **CIMT Trade Balance CAD** measures as values. Use `HSCode` as slicer or small multiples; show totals in CAD millions for clarity.
- Plot `PartnerCountry` versus **CIMT Imports CAD** to rank sourcing partners; US state rows sum to one United States country.
- Check 2025 total balance across all five selected HS6 codes: **−1,034,803,683 CAD**. The three HS2202 codes alone total **−913,756,529 CAD**. Avoid treating HS220190 as purely bottled water.

## Avoid errors
- Do not compute YoY across December 2022 / January 2023 before auditing NAPCS definitions.
- The two beverage labels exclude milk, hot-prepared drinks, and other categories as defined by the tables; do not present them as all beverages.
- Do not sum annual availability litres with monthly retail dollars.
- Set **Do not summarize** for source IDs and label fields; use category legends.
