# Power BI Desktop: start with authentic data immediately

The repository currently includes four **real, checked domestic-market CSVs**, plus three official HS6 imports CSVs:
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
5. Add a Blank Query and paste `powerbi/cimt_imports_from_github.pq`. Rename it `CIMTImports`. This reads the 3 original imports files and retains the US state field.
6. Select **Close & Apply**. For public source credentials choose **Anonymous**.
7. On report page **Domestic Retail**, choose a clustered column chart: Axis `year`; Legend `product_group`; Values SUM(`sales_cad_millions`). Add a **classification_vintage** slicer and visibly mark the 2023 break.
8. On page **Food Availability**, choose a line chart: X Axis `year`; Y Axis `value`; Legend `product`; add a filter `value_status = observed`. The 2024 gap must remain blank; bottled-water series has no observed values.
9. Save as `powerbi/Beverage_Market_Analytics.pbix` on your Windows PC; large PBIX files are intentionally excluded from Git until reviewed.

## Validation
- CIMT: 15,670 import observations across three HS6 codes, 72 months each; state-level US rows are not country-level subtotals.
- CIMT value 2025: 220210 = **742,467,960 CAD**; 220291 = **36,748,545 CAD**; 220299 = **917,338,369 CAD**. Calculate with `SUM(CIMTImports[ValueCAD])` filtered to the precise HS and Year.

- Retail has **144** rows (4 published source series × 36 months) and two categories each year.
- Unit is CAD **millions** in the M query, converted from published **thousands of CAD** by dividing by 1000.
- 2023 soft-drink annual sum = **4,540.377 million CAD**; 2025 = **4,883.636 million CAD**. Compare precisely matching filters.
- 2024 per-person availability is unavailable for the current 3 usable liquid series, **not zero**.

## Avoid errors
- Do not compute YoY across December 2022 / January 2023 before auditing NAPCS definitions.
- The two beverage labels exclude milk, hot-prepared drinks, and other categories as defined by the tables; do not present them as all beverages.
- Do not sum annual availability litres with monthly retail dollars.
- Set **Do not summarize** for source IDs and label fields; use category legends.
