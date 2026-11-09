-- Canadian Beverage Market Analytics | MySQL 8+
-- Published values and source measurement units are retained without guessed conversions.
CREATE DATABASE IF NOT EXISTS canadian_beverage_market
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE canadian_beverage_market;

CREATE TABLE IF NOT EXISTS dim_source (
  source_id VARCHAR(24) PRIMARY KEY,
  source_label VARCHAR(255) NOT NULL,
  classification_system VARCHAR(50) NOT NULL,
  source_url VARCHAR(600) NOT NULL
);
INSERT INTO dim_source VALUES
 ('20100017','Legacy retail commodity sales','NAPCS 2017','https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010001701'),
 ('20100080','Retail commodity sales','NAPCS 2022','https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010008001'),
 ('18100004','Consumer Price Index','CPI basket','https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401'),
 ('32100054','Food availability','Food availability classification','https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210005401'),
 ('16100048','Manufacturing sales','NAICS','https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1610004801'),
 ('12100176','Trade by industry all countries','NAICS','https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017601')
ON DUPLICATE KEY UPDATE source_label=VALUES(source_label),source_url=VALUES(source_url);

CREATE TABLE IF NOT EXISTS dim_period (
  reference_period VARCHAR(16) PRIMARY KEY,
  period_key INT NOT NULL,
  period_year SMALLINT NOT NULL,
  period_grain ENUM('monthly','quarterly','annual') NOT NULL,
  INDEX ix_year_grain(period_year,period_grain)
);

CREATE TABLE IF NOT EXISTS dim_series (
  series_id CHAR(64) PRIMARY KEY,
  source_id VARCHAR(24) NOT NULL,
  category_label VARCHAR(512) NOT NULL,
  geography VARCHAR(255) NOT NULL,
  unit_label VARCHAR(100) NOT NULL,
  scalar_factor VARCHAR(100) NOT NULL,
  vector_id VARCHAR(100) NOT NULL,
  coordinate VARCHAR(255) NOT NULL,
  dimensions_json JSON NOT NULL,
  -- Needs human confirmation against StatCan metadata.
  review_status ENUM('candidate','approved','excluded') NOT NULL DEFAULT 'candidate',
  mapped_product_group VARCHAR(100) NULL,
  reviewed_at DATETIME NULL,
  CONSTRAINT fk_series_source FOREIGN KEY (source_id) REFERENCES dim_source(source_id),
  INDEX ix_series_review(source_id,review_status),
  INDEX ix_series_product(mapped_product_group)
);

CREATE TABLE IF NOT EXISTS stg_statcan_observation (
  row_hash CHAR(64) PRIMARY KEY,
  source_id VARCHAR(24) NOT NULL,
  series_id CHAR(64) NOT NULL,
  period_key INT NOT NULL,
  reference_period VARCHAR(16) NOT NULL,
  period_year SMALLINT NOT NULL,
  period_grain ENUM('monthly','quarterly','annual') NOT NULL,
  category_label VARCHAR(512) NOT NULL,
  geography VARCHAR(255) NOT NULL,
  unit_label VARCHAR(100) NOT NULL,
  scalar_factor VARCHAR(100) NOT NULL,
  vector_id VARCHAR(100) NOT NULL,
  coordinate VARCHAR(255) NOT NULL,
  measure_value DECIMAL(24,8) NULL,
  status_code VARCHAR(50) NOT NULL,
  dimensions_json JSON NOT NULL,
  loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_stg_source_period(source_id,period_year),
  INDEX ix_stg_series(series_id)
);

-- Granular fact tables: never sum unlike units or mix classifications implicitly.
CREATE TABLE IF NOT EXISTS fact_retail_sales (
  series_id CHAR(64) NOT NULL,
  reference_period VARCHAR(16) NOT NULL,
  value_as_published DECIMAL(24,8) NULL,
  source_row_hash CHAR(64) NOT NULL,
  PRIMARY KEY(series_id,reference_period),
  FOREIGN KEY(series_id) REFERENCES dim_series(series_id),
  FOREIGN KEY(reference_period) REFERENCES dim_period(reference_period)
);
CREATE TABLE IF NOT EXISTS fact_price_index LIKE fact_retail_sales;
CREATE TABLE IF NOT EXISTS fact_food_availability LIKE fact_retail_sales;
CREATE TABLE IF NOT EXISTS fact_manufacturing LIKE fact_retail_sales;
CREATE TABLE IF NOT EXISTS fact_trade_industry LIKE fact_retail_sales;

-- MySQL CREATE TABLE LIKE copies indexes, not foreign key definitions.
ALTER TABLE fact_price_index
  ADD CONSTRAINT fk_cpi_series FOREIGN KEY(series_id) REFERENCES dim_series(series_id),
  ADD CONSTRAINT fk_cpi_period FOREIGN KEY(reference_period) REFERENCES dim_period(reference_period);
ALTER TABLE fact_food_availability
  ADD CONSTRAINT fk_avail_series FOREIGN KEY(series_id) REFERENCES dim_series(series_id),
  ADD CONSTRAINT fk_avail_period FOREIGN KEY(reference_period) REFERENCES dim_period(reference_period);
ALTER TABLE fact_manufacturing
  ADD CONSTRAINT fk_mfg_series FOREIGN KEY(series_id) REFERENCES dim_series(series_id),
  ADD CONSTRAINT fk_mfg_period FOREIGN KEY(reference_period) REFERENCES dim_period(reference_period);
ALTER TABLE fact_trade_industry
  ADD CONSTRAINT fk_trade_series FOREIGN KEY(series_id) REFERENCES dim_series(series_id),
  ADD CONSTRAINT fk_trade_period FOREIGN KEY(reference_period) REFERENCES dim_period(reference_period);

-- CIMT verified exports must be normalized to a known schema before importing.
CREATE TABLE IF NOT EXISTS dim_hs_product (
  hs_code VARCHAR(12) PRIMARY KEY,
  commodity_name VARCHAR(500) NOT NULL,
  classification_version VARCHAR(32) NOT NULL DEFAULT 'source-vintage-unverified',
  review_status ENUM('candidate','approved','excluded') NOT NULL DEFAULT 'candidate'
);
CREATE TABLE IF NOT EXISTS fact_hs_trade (
  trade_row_id CHAR(64) PRIMARY KEY,
  reference_period VARCHAR(16) NOT NULL,
  hs_code VARCHAR(12) NOT NULL,
  trade_flow ENUM('Import','Export') NOT NULL,
  partner_country VARCHAR(150) NOT NULL,
  clearance_geography VARCHAR(150) NOT NULL,
  value_cad DECIMAL(24,4) NOT NULL,
  quantity DECIMAL(24,6) NULL,
  quantity_unit VARCHAR(64) NOT NULL,
  source_note VARCHAR(500) NOT NULL,
  FOREIGN KEY(reference_period) REFERENCES dim_period(reference_period),
  FOREIGN KEY(hs_code) REFERENCES dim_hs_product(hs_code),
  INDEX ix_hs_period(reference_period,trade_flow),
  INDEX ix_hs_partner(partner_country,hs_code)
);
