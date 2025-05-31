{{ config(materialized='table') }}


SELECT
    cr.id AS review_id,
    b.id AS bank_id,
    br.id AS branch_id,
    l.id AS location_id,
    s.id AS sentiment_id,
    cr.clean_review AS review_text,
    cr.review_date_absolute AS review_date,
    cr.rating,
    cr.topic,
    cr.topic_meaning,
    cr.data_extraction_date
FROM transactional.clean_reviews cr
LEFT JOIN {{ ref('dim_bank') }} b ON cr.bank_name = b.bank_name
LEFT JOIN {{ ref('dim_branch') }} br ON cr.branch_name = br.branch_name
LEFT JOIN {{ ref('dim_location') }} l ON cr.location = l.location
LEFT JOIN {{ ref('dim_sentiment') }} s ON cr.sentiment = s.sentiment
GROUP BY
    cr.id, b.id, br.id, l.id, s.id,cr.clean_review, cr.review_date_absolute, cr.rating,cr.topic,cr.topic_meaning,cr.data_extraction_date