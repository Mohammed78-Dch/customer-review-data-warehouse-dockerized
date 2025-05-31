-- {{ config(materialized='table') }}


-- WITH base AS (
--     SELECT 
--         id,
--         bank_name,
--         branch_name,
--         location,
--         review_text,
--         rating,
--         review_date,
--         data_extraction_date
--     FROM public.bank_reviews
-- ),

-- remove_duplicates AS (
--     SELECT 
--         *, 
--         ROW_NUMBER() OVER (PARTITION BY location, review_date, review_text ORDER BY id) AS rn
--     FROM base
-- ),

-- cleaned AS (
--     SELECT 
--         id, 
--         bank_name, 
--         branch_name, 
--         location, 
--         review_text,

--         -- Étape 1 : Suppression des emojis et caractères spéciaux
--         regexp_replace(review_text, '[^\x20-\x7E\xA0-\xFF\x1000-\xFFFF]', '', 'g') AS step_1,

--         -- Étape 2 : Suppression de la ponctuation
--         regexp_replace(
--             regexp_replace(review_text, '[^\x20-\x7E\xA0-\xFF\x1000-\xFFFF]', '', 'g'),
--             '[[:punct:]]',
--             '',
--             'g'
--         ) AS step_2,

--         -- Étape 3 : Suppression des stop words (Anglais + Français)
--         regexp_replace(
--             '' || LOWER(
--                 regexp_replace(
--                     regexp_replace(review_text, '[^\x20-\x7E\xA0-\xFF\x1000-\xFFFF]', '', 'g'),
--                     '[[:punct:]]', '', 'g'
--                 )
--             ) || ' ',  -- Ajout d'espaces pour bien isoler les mots
--             ' (a|is|the|an|and|are|as|at|be|but|by|for|if|in|into|it|no|not|of|on|or|such|that|their|then|there|these|they|this|to|was|will|with|un|une|le|la|les|de|du|des|et|à|pour|avec|ce|ces|dans|par|sur|au|aux|en|est|sont|se|qui|que|quoi|dont|où|quand|comment|car|mais|donc|or|ni|soit|tandis|pendant|alors|comme|avant|après) ',
--             ' ',
--             'g'
--         ) AS clean_review,

--         -- Remplacement des notes NULL par la moyenne des notes existantes
--         COALESCE(rating, (SELECT AVG(rating) FROM base WHERE rating IS NOT NULL)) AS rating,

--         -- Remplacement des avis NULL par un texte par défaut
--         COALESCE(review_text, 'Avis non disponible') AS review_text_filled,

--         review_date,
--         data_extraction_date
--     FROM remove_duplicates
--     WHERE rn = 1
-- )

-- SELECT id, bank_name, branch_name, location, review_text, clean_review, review_date, rating,data_extraction_date
-- FROM cleaned

-- modifier site code pas insert id qui de table public.bank_reviews faire une identifient new et unique pour chaque ligne qui incrémenter automatiquement pas sélectionner si un ligne pas de texte views


-- {{ config(materialized='table') }}

-- WITH base AS (
--     SELECT 
--         id,
--         bank_name,
--         branch_name,
--         location,
--         review_text,
--         rating,
--         review_date,
--         data_extraction_date
--     FROM public.bank_reviews
-- ),

-- remove_duplicates AS (
--     SELECT 
--         *, 
--         ROW_NUMBER() OVER (PARTITION BY location, review_date, review_text ORDER BY id) AS rn
--     FROM base
-- ),

-- clean_text AS (
--     SELECT 
--         id, 
--         bank_name, 
--         branch_name, 
--         location, 
--         review_text,
        
--         -- Step 1: Remove emojis and special characters
--         regexp_replace(review_text, '[^\x20-\x7E\xA0-\xFF\x1000-\xFFFF]', '', 'g') AS no_special_chars,

--         -- Step 2: Remove punctuation
--         regexp_replace(review_text, '[[:punct:]]', '', 'g') AS no_punctuation
--     FROM remove_duplicates
--     WHERE rn = 1
-- ),

-- remove_stopwords AS (
--     SELECT 
--         id, 
--         bank_name, 
--         branch_name, 
--         location, 
--         review_text,
        
--         -- Apply stop word filtering
--         regexp_replace(
--             LOWER(no_punctuation),
--             ' (a|is|the|an|and|are|as|at|be|but|by|for|if|in|into|it|no|not|of|on|or|such|that|their|then|there|these|they|this|to|was|will|with|un|une|le|la|les|de|du|des|et|à|pour|avec|ce|ces|dans|par|sur|au|aux|en|est|sont|se|qui|que|quoi|dont|où|quand|comment|car|mais|donc|or|ni|soit|tandis|pendant|alors|comme|avant|après) ',
--             ' ',
--             'g'
--         ) AS clean_review
--     FROM clean_text
-- ),

-- final_data AS (
--     SELECT 
--         r.id, 
--         r.bank_name, 
--         r.branch_name, 
--         r.location, 
--         r.review_text,
--         c.clean_review,

--         -- Replace NULL ratings with average rating (computed once for efficiency) and cast to integer
--         CAST(COALESCE(r.rating, AVG(r.rating) OVER ()) AS INT) AS rating,

--         -- Replace NULL reviews with default text
--         COALESCE(r.review_text, 'Avis non disponible') AS review_text_filled,

--         r.review_date,
--         r.data_extraction_date
--     FROM remove_stopwords c
--     JOIN remove_duplicates r ON c.id = r.id
-- )

-- SELECT id, bank_name, branch_name, location, review_text, clean_review, review_date, rating, data_extraction_date
-- FROM final_data

{{ config(materialized='table') }}

-- Define the main_banks list as a CTE for filtering
WITH main_banks_list AS (
    SELECT unnest(ARRAY[
        'Bank Al-Maghrib', 'بنك المغرب',
        'Attijariwafa Bank', 'التجاري وفا بنك',
        'Banque Populaire', 'البنك الشعبي',
        'Bank of Africa', 'بنك أفريقيا',
        'BMCE Bank', 'بنك BMCE',
        'Crédit du Maroc', 'القرض العقاري',
        'Société Générale Maroc', 'البنك العام المغربي',
        'BMCI', 'بنك BMCI',
        'CFG Bank', 'CFG بنك',
        'CIH Bank', 'بنك CIH',
        'Crédit Agricole du Maroc', 'القرض الفلاحي للمغرب',
        'Al Barid Bank', 'البريد بنك',
        'Arab Bank Maroc', 'البنك العربي المغربي',
        'Citibank Morocco', 'سيتي بنك المغرب',
        'Union Marocaine de Banques', 'الاتحاد المغربي للبنوك',
        'Umnia Bank', 'بنك أمين',
        'Bank Al Yousr', 'بنك اليسر',
        'BTI Bank', 'بنك BTI',
        'Al Akhdar Bank', 'البنك الأخضر',
        'Bank Assafa', 'بنك الصفاء',
        'CDG Capital', 'CDG كابيتال',
        'Attijari Finances Corp.', 'التجاري للتمويل',
        'BMCE Capital', 'BMCE كابيتال',
        'Upline Group', 'مجموعة أوبلاين',
        'Casablanca Finance Group', 'مجموعة الدار البيضاء المالية',
        'Attijari International Bank', 'التجاري بنك الدولي',
        'Banque Internationale de Tanger', 'البنك الدولي لطنجة',
        'BMCI - Banque Offshore', 'BMCI - البنك الخارجي',
        'Chaabi International Bank', 'الشعبي بنك الدولي',
        'Société Générale Banque Offshore', 'البنك العام الخارجي',
        'BMCE Offshore', 'BMCE البنك الخارجي'
    ]) AS bank_name
),

base AS (
    SELECT 
        -- Generate a new unique ID using ROW_NUMBER()
        ROW_NUMBER() OVER (ORDER BY review_date) AS temp_id,
        bank_name,
        branch_name,
        location,
        review_text,
        rating,
        review_date,
        data_extraction_date
    FROM public.all_bank_reviews
    WHERE review_text IS NOT NULL AND review_text <> '' -- Exclude rows with empty/null review_text
),

filtered_base AS (
    SELECT 
        b.temp_id,
        b.bank_name,
        -- Update branch_name to include location only if branch_name is NULL/empty or equal to bank_name
        CASE 
            WHEN b.branch_name IS NULL OR b.branch_name = '' 
                 THEN CONCAT(b.bank_name, ' - ', b.location)
            WHEN LOWER(b.branch_name) = LOWER(b.bank_name) 
                 THEN CONCAT(b.bank_name, ' - ', b.location)
            ELSE b.branch_name
        END AS branch_name,
        b.location,
        b.review_text,
        b.rating,
        b.review_date,
        b.data_extraction_date
    FROM base b
    -- INNER JOIN main_banks_list m ON LOWER(b.bank_name) = LOWER(m.bank_name) -- Filter by main_banks list
),

clean_text AS (
    SELECT 
        temp_id,
        bank_name,
        branch_name,
        location,
        review_text,
        
        -- Step 1: Remove emojis and special characters
        regexp_replace(review_text, '[^\x20-\x7E\xA0-\xFF\x1000-\xFFFF]', '', 'g') AS no_special_chars,

        -- Step 2: Remove punctuation
        regexp_replace(review_text, '[[:punct:]]', '', 'g') AS no_punctuation
    FROM filtered_base
),

remove_stopwords AS (
    SELECT 
        temp_id,
        bank_name,
        branch_name,
        location,
        review_text,
        
        -- Apply stop word filtering
        regexp_replace(
            LOWER(no_punctuation),
            ' (a|is|the|an|and|are|as|at|be|but|by|for|if|in|into|it|no|not|of|on|or|such|that|their|then|there|these|they|this|to|was|will|with|un|une|le|la|les|de|du|des|et|à|pour|avec|ce|ces|dans|par|sur|au|aux|en|est|sont|se|qui|que|quoi|dont|où|quand|comment|car|mais|donc|or|ni|soit|tandis|pendant|alors|comme|avant|après) ',
            ' ',
            'g'
        ) AS clean_review
    FROM clean_text
),

final_data AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY r.temp_id) AS id, -- Generate continuous ID
        r.bank_name,
        r.branch_name,
        r.location,
        r.review_text,
        c.clean_review,

        -- Replace NULL ratings with average rating (computed once for efficiency) and cast to integer
        CAST(COALESCE(r.rating, AVG(r.rating) OVER ()) AS INT) AS rating,

        r.review_date,
        r.data_extraction_date
    FROM remove_stopwords c
    JOIN filtered_base r ON c.temp_id = r.temp_id
    WHERE c.clean_review IS NOT NULL AND TRIM(c.clean_review) <> '' -- Exclude rows with empty clean_review
)

SELECT id, bank_name, branch_name, location, review_text, clean_review, review_date, rating, data_extraction_date
FROM final_data