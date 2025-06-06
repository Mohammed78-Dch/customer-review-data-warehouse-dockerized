import psycopg2
import json
from connect_to_db import connect_to_aiven_db


import os

base_dir = os.path.dirname(__file__)

# Construire le chemin relatif sans le répéter
avis_path = os.path.join(base_dir, 'avis.json')
# Récupérer les credentials depuis les variables d'environnement
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_NAME = os.getenv("DB_NAME", "project_data_wherhouse")
# DB_USER = os.getenv("DB_USER", "user_project")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "2002")

# Fonction pour insérer les données dans PostgreSQL
def insert_data_to_postgresql(**kwargs):
    try:
        # conn = psycopg2.connect(
        #     host=DB_HOST,
        #     database=DB_NAME,
        #     user=DB_USER,
        #     password=DB_PASSWORD
        # )
        conn = connect_to_aiven_db()
        if not conn:
            raise Exception("Échec de la connexion à la base de données.")
        cursor = conn.cursor()

        # Appeler la fonction de scraping
        # scraped_data = scrape_bank_reviews()
        
        # Charger le fichier JSON des banques
        with open(avis_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Création de la table enriched si elle n'existe pas
        cursor.execute("""
         CREATE TABLE IF NOT EXISTS public.all_bank_reviews  (
            id integer NOT NULL DEFAULT nextval('bank_reviews_id_seq'::regclass),
            bank_name text COLLATE pg_catalog."default" NOT NULL,
            branch_name text COLLATE pg_catalog."default" NOT NULL,
            location text COLLATE pg_catalog."default" NOT NULL,
            review_text text COLLATE pg_catalog."default",
            rating double precision,
            review_date text NOT NULL,
            data_extraction_date date DEFAULT CURRENT_DATE,
            CONSTRAINT bank_reviews_pkey PRIMARY KEY (id),
            CONSTRAINT unique_review UNIQUE (location, review_date, review_text)
        );
        """)
        conn.commit()

        # Extraire les avis des banques

        

        for bank_id, bank_info in data.items():
            bank_name = bank_info.get("Bank name", "")
            branch_name = bank_info.get("branch name", "")
            location = bank_info.get("location", "")

            for review in bank_info.get("avis", []):
                review_text = review.get("avis_text", "")
                review_date = review.get("date", "2000-01-01")  # Valeur par défaut
                review_rating = float(review.get("rating", "0").replace(",", ".") or 0)

                cursor.execute("""
                    INSERT INTO public.all_bank_reviews (bank_name, branch_name, location, review_text, rating, review_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (location, review_date, review_text) DO NOTHING
                """, (bank_name, branch_name, location, review_text, review_rating, review_date))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Données insérées avec succès.")

    except Exception as e:
        print(f"❌ Erreur PostgreSQL : {e}")
     