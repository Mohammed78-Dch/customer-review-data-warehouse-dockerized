# import psycopg2
# from textblob import TextBlob

# # Connexion PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# # Ajouter la colonne sentiment si elle n'existe pas
# cur.execute("""
#     ALTER TABLE transactional.clean_reviews 
#     ADD COLUMN IF NOT EXISTS sentiment TEXT;
# """)
# conn.commit()

# # Récupérer les avis nettoyés
# cur.execute("SELECT id, clean_review FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
# rows = cur.fetchall()

# # Analyse de sentiment
# for row in rows:
#     review_id = row[0]
#     text = row[1]

#     try:
#         sentiment_score = TextBlob(text).sentiment.polarity
#         if sentiment_score > 0.1:
#             sentiment = "Positive"
#         elif sentiment_score < -0.1:
#             sentiment = "Negative"
#         else:
#             sentiment = "Neutral"
#     except Exception:
#         sentiment = "Unknown"

#     # Mise à jour de la table enrichie
#     cur.execute("""
#         UPDATE transactional.clean_reviews 
#         SET sentiment = %s 
#         WHERE id = %s;
#     """, (sentiment, review_id))

# conn.commit()
# cur.close()
# conn.close()

# print("✅ Analyse de sentiment appliquée avec succès.")



# import psycopg2
# from textblob import TextBlob
# from nltk.sentiment import SentimentIntensityAnalyzer
# from vaderSentiment_fr.vaderSentiment import SentimentIntensityAnalyzer as VaderFr
# from camel_tools.sentiment import SentimentAnalyzer
# import nltk
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# # Download necessary resources
# nltk.download('vader_lexicon')

# # Initialize Sentiment Analyzers
# sia_en = SentimentIntensityAnalyzer()  # English VADER
# sia_fr = VaderFr()  # French VADER
# arabic_sa = SentimentAnalyzer.pretrained()  # Arabic sentiment analyzer

# # PostgreSQL Connection
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# try:
#     # Ensure the sentiment column exists
#     cur.execute("""
#         ALTER TABLE transactional.clean_reviews 
#         ADD COLUMN IF NOT EXISTS sentiment TEXT;
#     """)
#     conn.commit()

#     # Fetch cleaned reviews
#     cur.execute("SELECT id, clean_review, language FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
#     rows = cur.fetchall()

#     # Prepare batch update
#     update_query = """
#         UPDATE transactional.clean_reviews 
#         SET sentiment = %s 
#         WHERE id = %s;
#     """
#     batch_data = []

#     for row in rows:
#         review_id, text, lang = row

#         try:
#             if lang == "en":  # English → Use VADER
#                 sentiment_score = sia_en.polarity_scores(text)['compound']
#             elif lang == "fr":  # French → Use VADER-FR
#                 sentiment_score = sia_fr.polarity_scores(text)['compound']
#             elif lang == "ar":  # Arabic → Use CAMeL Tools
#                 sentiment_raw = arabic_sa.predict(text)  # Returns "positive", "negative", "neutral"
#                 sentiment = sentiment_raw.capitalize()
#                 batch_data.append((sentiment, review_id))
#                 continue
#             else:  # Default to TextBlob
#                 sentiment_score = TextBlob(text).sentiment.polarity

#             # Classify sentiment
#             sentiment = "Positive" if sentiment_score > 0.1 else "Negative" if sentiment_score < -0.1 else "Neutral"
#             batch_data.append((sentiment, review_id))

#         except Exception as e:
#             logging.error(f"Error processing review {review_id} (Language: {lang}, Text: {text[:50]}...): {e}")
#             batch_data.append(("Unknown", review_id))

#     # Batch update database
#     cur.executemany(update_query, batch_data)
#     conn.commit()

# finally:
#     cur.close()
#     conn.close()

# logging.info("✅ Sentiment analysis applied successfully!")



import psycopg2
from transformers import pipeline
import logging
from connect_to_db import connect_to_aiven_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# PostgreSQL Connection
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
conn = connect_to_aiven_db()
if not conn:
    raise Exception("Failed to connect to the database.")
cur = conn.cursor()

try:
    # Ensure the sentiment column exists
    cur.execute("""
        ALTER TABLE transactional.clean_reviews 
        ADD COLUMN IF NOT EXISTS sentiment TEXT;
    """)
    conn.commit()

    # Fetch cleaned reviews
    cur.execute("SELECT id, clean_review FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
    rows = cur.fetchall()

    # Initialize a multilingual sentiment analysis pipeline using Hugging Face's transformers
    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

    # Prepare batch update
    update_query = """
        UPDATE transactional.clean_reviews 
        SET sentiment = %s 
        WHERE id = %s;
    """
    batch_data = []

    for row in rows:
        review_id, text = row

        try:
            # Perform sentiment analysis
            result = sentiment_analyzer(text)[0]
            label = result['label']
            score = result['score']

            # Map labels to simpler sentiment categories
            if label in ["1 star", "2 stars"]:
                sentiment = "Negative"
            elif label in ["4 stars", "5 stars"]:
                sentiment = "Positive"
            else:  # 3 stars
                sentiment = "Neutral"

            batch_data.append((sentiment, review_id))

        except Exception as e:
            logging.error(f"Error processing review {review_id} (Text: {text[:50]}...): {e}")
            batch_data.append(("Unknown", review_id))

    # Batch update database
    cur.executemany(update_query, batch_data)
    conn.commit()

finally:
    cur.close()
    conn.close()

logging.info("✅ Sentiment analysis applied successfully!")


