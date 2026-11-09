USE canadian_beverage_market;
CREATE OR REPLACE VIEW vw_retail_approved AS
SELECT f.series_id,f.reference_period,p.period_year,p.period_grain,
  d.source_id,d.mapped_product_group,d.category_label,d.geography,
  d.unit_label,d.scalar_factor,f.value_as_published
FROM fact_retail_sales f JOIN dim_series d USING(series_id)
JOIN dim_period p USING(reference_period)
WHERE d.review_status='approved';

CREATE OR REPLACE VIEW vw_cpi_approved AS
SELECT f.series_id,f.reference_period,p.period_year,p.period_grain,
  d.category_label,d.mapped_product_group,d.geography,d.unit_label,
  d.scalar_factor,f.value_as_published
FROM fact_price_index f JOIN dim_series d USING(series_id)
JOIN dim_period p USING(reference_period)
WHERE d.review_status='approved';

CREATE OR REPLACE VIEW vw_availability_approved AS
SELECT f.series_id,f.reference_period,p.period_year,p.period_grain,
  d.category_label,d.mapped_product_group,d.geography,d.unit_label,
  d.scalar_factor,f.value_as_published
FROM fact_food_availability f JOIN dim_series d USING(series_id)
JOIN dim_period p USING(reference_period)
WHERE d.review_status='approved';

CREATE OR REPLACE VIEW vw_manufacturing_approved AS
SELECT f.series_id,f.reference_period,p.period_year,p.period_grain,
  d.category_label,d.mapped_product_group,d.geography,d.unit_label,
  d.scalar_factor,f.value_as_published
FROM fact_manufacturing f JOIN dim_series d USING(series_id)
JOIN dim_period p USING(reference_period)
WHERE d.review_status='approved';

CREATE OR REPLACE VIEW vw_trade_industry_approved AS
SELECT f.series_id,f.reference_period,p.period_year,p.period_grain,
  d.category_label,d.mapped_product_group,d.geography,d.unit_label,
  d.scalar_factor,f.value_as_published
FROM fact_trade_industry f JOIN dim_series d USING(series_id)
JOIN dim_period p USING(reference_period)
WHERE d.review_status='approved';

CREATE OR REPLACE VIEW vw_hs_trade AS
SELECT f.reference_period,p.period_year,f.hs_code,d.commodity_name,
  d.classification_version,d.review_status,f.trade_flow,
  f.partner_country,f.clearance_geography,f.value_cad,
  f.quantity,f.quantity_unit,f.source_note
FROM fact_hs_trade f JOIN dim_hs_product d USING(hs_code)
JOIN dim_period p USING(reference_period)
WHERE d.review_status='approved';

-- Explicitly country-level ONLY, Canada clearance and excluding World totals.
-- Not a market share of Canadian consumption.
CREATE OR REPLACE VIEW vw_hs_import_partner_canada AS
SELECT reference_period,period_year,hs_code,commodity_name,partner_country,
       value_cad,quantity,quantity_unit
FROM vw_hs_trade
WHERE trade_flow='Import'
  AND clearance_geography='Canada'
  AND LOWER(partner_country) NOT IN ('world','all countries','total','all trading partners');
