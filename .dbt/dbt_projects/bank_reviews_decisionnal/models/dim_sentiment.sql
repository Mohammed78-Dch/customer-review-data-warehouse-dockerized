{{ config(materialized='table') }}


WITH sentiment_analysis AS (
    SELECT DISTINCT 
          sentiment
    FROM transactional.clean_reviews
)
SELECT
    ROW_NUMBER() OVER () AS id, -- Identifiant unique pour chaque sentiment
    sentiment
FROM sentiment_analysis