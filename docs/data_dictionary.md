# Data dictionary

## Core entities
- `dim_source`: StatCan PID, source name, original classification system and URL.
- `dim_period`: exact period string, numeric sortable period key, year and frequency.
- `dim_series`: source-specific VECTOR/COORDINATE plus original category, geography, units, scalar factor and review state. **Not** a common product code across sources.
- `stg_statcan_observation`: reproducible per-series source observation, retaining original published units and missing values.
- `fact_retail_sales`: monthly series from original NAPCS retail vintages, materialized after manual approval.
- `fact_price_index`: CPI index observations, materialized after approval.
- `fact_food_availability`: annual published availability observations, materialized after approval.
- `fact_manufacturing`: industry manufacturing observations, materialized after approval.
- `fact_trade_industry`: NAICS industry-level international merchandise trade observations, not partner-level HS.
- `dim_hs_product` and `fact_hs_trade`: imported verified CIMT commodity-level imports and Total exports. Trade rows preserve import/export flow, clearance geography, partner, partner state (including US states), CAD values, quantity and original quantity unit.

## Keys and grain
- Series key = SHA-256 of source ID, vector/coordinate or dimensions, geography, published unit and scalar factor.
- Observation key = SHA-256(series key, original reference period).
- Fact tables = one reviewed series × one reference period.
- HS trade = one reference period × HS code × flow × partner country × partner state × clearance geography × reported measure (after normalization and deduplication).
- An annual value must not be multiplied by 12 to manufacture monthly coverage.

## Interpretation
`value_as_published` is intentionally not named 'sales_cad': verify unit, source scalar factor, and classification before monetary conversion. Do not claim market revenue by summing unrelated series.
