{{ config(materialized='table') }}

WITH unique_branches AS (
    SELECT DISTINCT
        branch_name
    FROM transactional.clean_reviews
)
SELECT
    ROW_NUMBER() OVER () AS id,
    branch_name
FROM unique_branches