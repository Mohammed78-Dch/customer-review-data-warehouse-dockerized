{{ config(materialized='table') }}

WITH unique_locations AS (
    SELECT DISTINCT
        location
    FROM transactional.clean_reviews
)
SELECT
    ROW_NUMBER() OVER () AS id,
    location
FROM unique_locations