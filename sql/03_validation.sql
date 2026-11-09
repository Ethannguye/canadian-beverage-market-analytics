USE canadian_beverage_market;
-- Row counts (0 approved facts initially is EXPECTED).
SELECT 'staging' dataset,COUNT(*) rows_loaded FROM stg_statcan_observation
UNION ALL SELECT 'retail',COUNT(*) FROM fact_retail_sales
UNION ALL SELECT 'cpi',COUNT(*) FROM fact_price_index
UNION ALL SELECT 'availability',COUNT(*) FROM fact_food_availability
UNION ALL SELECT 'manufacturing',COUNT(*) FROM fact_manufacturing
UNION ALL SELECT 'industry_trade',COUNT(*) FROM fact_trade_industry
UNION ALL SELECT 'hs_trade',COUNT(*) FROM fact_hs_trade;

-- Missing values and coverage by raw source, WITHOUT implying all beverage categories exist.
SELECT source_id, MIN(reference_period) first_period,
       MAX(reference_period) last_period,
       COUNT(*) rows_seen, SUM(measure_value IS NULL) null_values,
       COUNT(DISTINCT series_id) distinct_series
FROM stg_statcan_observation GROUP BY source_id;

-- Review status: fact data require approved series.
SELECT source_id,review_status,COUNT(*) series_count
FROM dim_series GROUP BY source_id,review_status ORDER BY source_id,review_status;

-- Detection of accidentally duplicated time-series observations across staging:
SELECT source_id,series_id,reference_period,COUNT(*) row_count
FROM stg_statcan_observation
GROUP BY source_id,series_id,reference_period
HAVING COUNT(*) > 1 LIMIT 100;

-- Numeric units/scale must be reviewed before aggregation:
SELECT source_id,unit_label,scalar_factor,COUNT(*) series_count
FROM dim_series GROUP BY source_id,unit_label,scalar_factor
ORDER BY source_id,series_count DESC;

-- HS trade granularity and geography; 'World' subtotals must not mix with countries.
SELECT trade_flow,clearance_geography,partner_country,COUNT(*) row_count
FROM fact_hs_trade GROUP BY trade_flow,clearance_geography,partner_country
ORDER BY row_count DESC LIMIT 100;
