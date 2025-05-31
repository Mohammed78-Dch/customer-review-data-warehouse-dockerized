{{ config(materialized='table') }}

WITH unique_banks AS (
    SELECT DISTINCT
        bank_name
    FROM transactional.clean_reviews
)
SELECT
    ROW_NUMBER() OVER () AS id,
    bank_name
FROM unique_banks