


import psycopg2
from transformers import pipeline
import logging
from connect_to_db import connect_to_aiven_db

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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


