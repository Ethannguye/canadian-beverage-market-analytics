# Methodology and interpretation guardrails

**Window:** 2020-01 to 2025-12 inclusive. Monthly indicators should be date-keyed (YYYY-MM); annual availability is keyed by year, and must not be repeated as independent monthly observations.

**Population:** Canada's non-alcoholic beverage products where source classification explicitly supports inclusion. Do not silently include alcohol, ice, foods, or overly broad categories.

**Classification breaks:** Retail commodity statistics switched to NAPCS 2022 at January 2023. Maintain source code, system, vintage, and mapping confidence in the data model. Comparisons across the break require demonstrated equivalence.

**Trade classification:** HS chapters/headings 2009 (juice), 2201 (waters), and 2202 (flavoured waters and other non-alcoholic beverages) are initial *candidate* groups; review detailed commodity definitions and their vintage. Avoid counting overlapping totals, such as a heading and its subheadings together.

**Currency and unit:** Preserve reported value units, quantity units, scale factor, seasonal adjustment, and price basis. Do not sum across incompatible units.

**Geography:** Some trade provincial figures reflect province of customs clearance, not final destination. Compare geography only at the level established by the underlying table.

**Revision policy:** Treat downloaded tables as snapshots; log download timestamp, table PID, URL, and sha256. Update backfilled revisions intentionally.

**Validation gates:** Schema present; date in scope; no duplicate natural keys; no unwanted broader product codes; source units consistent; time coverage and missingness documented; concordance audited.

**No fabricated outputs:** Empty placeholders and SQL/DAX templates must not be interpreted as final results until validated 2020–2025 rows are loaded.
