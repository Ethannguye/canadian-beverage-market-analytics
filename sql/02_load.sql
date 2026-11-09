-- Use after sql/01_schema.sql AND etl/load_mysql.py.
USE canadian_beverage_market;
DROP PROCEDURE IF EXISTS sp_materialize_approved_facts;
DELIMITER $$
CREATE PROCEDURE sp_materialize_approved_facts()
BEGIN
  -- No auto-approval: values only enter facts if series review_status='approved'.
  INSERT INTO fact_retail_sales(series_id,reference_period,value_as_published,source_row_hash)
    SELECT s.series_id,s.reference_period,s.measure_value,s.row_hash
    FROM stg_statcan_observation s JOIN dim_series d ON d.series_id=s.series_id
    WHERE d.review_status='approved' AND s.source_id IN ('20100017','20100080')
    ON DUPLICATE KEY UPDATE value_as_published=VALUES(value_as_published),
                            source_row_hash=VALUES(source_row_hash);

  INSERT INTO fact_price_index(series_id,reference_period,value_as_published,source_row_hash)
    SELECT s.series_id,s.reference_period,s.measure_value,s.row_hash
    FROM stg_statcan_observation s JOIN dim_series d ON d.series_id=s.series_id
    WHERE d.review_status='approved' AND s.source_id='18100004'
    ON DUPLICATE KEY UPDATE value_as_published=VALUES(value_as_published),
                            source_row_hash=VALUES(source_row_hash);

  INSERT INTO fact_food_availability(series_id,reference_period,value_as_published,source_row_hash)
    SELECT s.series_id,s.reference_period,s.measure_value,s.row_hash
    FROM stg_statcan_observation s JOIN dim_series d ON d.series_id=s.series_id
    WHERE d.review_status='approved' AND s.source_id='32100054'
    ON DUPLICATE KEY UPDATE value_as_published=VALUES(value_as_published),
                            source_row_hash=VALUES(source_row_hash);

  INSERT INTO fact_manufacturing(series_id,reference_period,value_as_published,source_row_hash)
    SELECT s.series_id,s.reference_period,s.measure_value,s.row_hash
    FROM stg_statcan_observation s JOIN dim_series d ON d.series_id=s.series_id
    WHERE d.review_status='approved' AND s.source_id='16100048'
    ON DUPLICATE KEY UPDATE value_as_published=VALUES(value_as_published),
                            source_row_hash=VALUES(source_row_hash);

  INSERT INTO fact_trade_industry(series_id,reference_period,value_as_published,source_row_hash)
    SELECT s.series_id,s.reference_period,s.measure_value,s.row_hash
    FROM stg_statcan_observation s JOIN dim_series d ON d.series_id=s.series_id
    WHERE d.review_status='approved' AND s.source_id='12100176'
    ON DUPLICATE KEY UPDATE value_as_published=VALUES(value_as_published),
                            source_row_hash=VALUES(source_row_hash);
END$$
DELIMITER ;

-- Manual-review queue: inspect classification and units BEFORE approving anything.
SELECT series_id,source_id,category_label,geography,unit_label,scalar_factor,
       vector_id,coordinate,review_status
FROM dim_series
WHERE review_status='candidate'
ORDER BY source_id,category_label,geography LIMIT 250;

-- Example only AFTER confirmation of exact series id; never approve all candidates.
-- UPDATE dim_series SET review_status='approved', mapped_product_group='Soft drinks',
--   reviewed_at=NOW() WHERE series_id='<REVIEWED_REAL_SERIES_ID>';
-- CALL sp_materialize_approved_facts();
