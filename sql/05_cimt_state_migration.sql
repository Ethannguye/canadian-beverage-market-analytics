-- Run ONCE only on an existing database built before partner_state was introduced.
-- Newly initialized databases from 01_schema.sql ALREADY include partner_state.
USE canadian_beverage_market;
ALTER TABLE fact_hs_trade
  ADD COLUMN partner_state VARCHAR(100) NOT NULL DEFAULT 'N/A' AFTER partner_country;
-- Existing HS rows may have lost US state distinctions and need a clean,
-- reviewed reimport from original CSV; do not assume 'N/A' is a correct state.
