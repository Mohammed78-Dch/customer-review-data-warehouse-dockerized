# from langdetect import detect
# import psycopg2

# # Connexion PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )

# cur = conn.cursor()

# # Vérifier que la table enriched existe
# cur.execute("""
# CREATE TABLE IF NOT EXISTS transactional.clean_reviews (
#     id SERIAL PRIMARY KEY,
#     bank_name TEXT,
#     branch_name TEXT,
#     location TEXT,
#     review_text TEXT,
#     clean_review TEXT,
#     rating NUMERIC,
#     review_date DATE,
#     data_extraction_date DATE,
#     language TEXT
# );
# """)
# conn.commit()

# # Récupérer les avis
# cur.execute("SELECT id, bank_name, branch_name, location, review_text, clean_review, rating, review_date,data_extraction_date FROM transactional.clean_reviews WHERE review_text IS NOT NULL;")
# rows = cur.fetchall()

# # Détection de langue & insertion
# for row in rows:
#     review_id = row[0]
#     bank_name = row[1]
#     branch_name = row[2]
#     location = row[3]
#     text = row[4]
#     clean_review = row[5]
#     rating = row[6]
#     review_date = row[7]
#     data_extraction_date =row[8]

#     try:
#         lang = detect(text)
#     except:
#         lang = "unknown"

#     # Insérer les données enrichies
#     cur.execute("""
#         INSERT INTO transactional.clean_reviews (id, bank_name, branch_name, location, review_text, clean_review, rating, review_date,data_extraction_date, language)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s)
#         ON CONFLICT (id) DO UPDATE 
#         SET language = EXCLUDED.language;
#     """, (review_id, bank_name, branch_name, location, text, clean_review, rating, review_date,data_extraction_date, lang))

# conn.commit()
# cur.close()
# conn.close()

# print("✅ Langue detectée avec succès.")


# import fasttext
# import psycopg2

# # Charger le modèle FastText pour la détection de langue
# model_path = "/home/mohammed/airflow/scripts/lid.176.bin"

# model = fasttext.load_model(model_path)

# # Connexion à PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# # Création de la table enriched si elle n'existe pas
# cur.execute("""
# CREATE TABLE IF NOT EXISTS transactional.clean_reviews (
#     id SERIAL PRIMARY KEY,
#     bank_name TEXT,
#     branch_name TEXT,
#     location TEXT,
#     review_text TEXT,
#     clean_review TEXT,
#     rating NUMERIC,
#     review_date DATE,
#     data_extraction_date DATE,
#     language TEXT
# );
# """)
# conn.commit()

# # Récupérer les avis depuis la table source
# cur.execute("""
# SELECT id, bank_name, branch_name, location, review_text, clean_review, rating, review_date, data_extraction_date 
# FROM transactional.clean_reviews 
# WHERE review_text IS NOT NULL;
# """)
# rows = cur.fetchall()

# batch_size = 500  # Taille du batch pour optimiser l'insertion
# batch_data = []

# # Détection de la langue et préparation des données pour l'insertion
# for row in rows:
#     review_id, bank_name, branch_name, location, text, clean_review, rating, review_date, data_extraction_date = row

#     try:
#         lang = model.predict(text)[0][0].replace("__label__", "")  # Détection de la langue
#     except:
#         lang = "unknown"

#     batch_data.append((review_id, bank_name, branch_name, location, text, clean_review, rating, review_date, data_extraction_date, lang))

#     # Insertion par batch
#     if len(batch_data) >= batch_size:
#         cur.executemany("""
#             INSERT INTO transactional.clean_reviews 
#             (id, bank_name, branch_name, location, review_text, clean_review, rating, review_date, data_extraction_date, language)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (id) DO UPDATE 
#             SET language = EXCLUDED.language;
#         """, batch_data)
#         conn.commit()
#         batch_data = []  # Réinitialiser le batch

# # Insérer les données restantes
# if batch_data:
#     cur.executemany("""
#         INSERT INTO transactional.clean_reviews 
#         (id, bank_name, branch_name, location, review_text, clean_review, rating, review_date, data_extraction_date, language)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         ON CONFLICT (id) DO UPDATE 
#         SET language = EXCLUDED.language;
#     """, batch_data)
#     conn.commit()

# cur.close()
# conn.close()
# print("✅ Détection de langue et insertion terminées avec succès ! 🚀")


# import fasttext
# import psycopg2

# # Charger le modèle FastText pour la détection de langue
# model_path = "/home/mohammed/airflow/scripts/lid.176.bin"
# model = fasttext.load_model(model_path)

# # Connexion à PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# # Vérifier si la colonne 'language' existe dans la table cible
# cur.execute("""
#     SELECT EXISTS (
#         SELECT 1
#         FROM information_schema.columns
#         WHERE table_name = 'clean_reviews'
#           AND column_name = 'language'
#     );
# """)
# language_column_exists = cur.fetchone()[0]

# # Ajouter la colonne 'language' si elle n'existe pas
# if not language_column_exists:
#     cur.execute("""
#         ALTER TABLE transactional.clean_reviews
#         ADD COLUMN language TEXT;
#     """)
#     conn.commit()
#     print("✅ Colonne 'language' ajoutée à la table 'clean_reviews'.")

# # Récupérer les avis où la colonne 'language' est NULL ou non définie
# cur.execute("""
#     SELECT id, review_text
#     FROM transactional.clean_reviews
#     WHERE language IS NULL OR language = '';
# """)
# rows = cur.fetchall()

# batch_size = 500  # Taille du batch pour optimiser les mises à jour
# batch_data = []

# # Détection de la langue et préparation des données pour la mise à jour
# for row in rows:
#     review_id, text = row

#     try:
#         lang = model.predict(text)[0][0].replace("__label__", "")  # Détection de la langue
#     except:
#         lang = "unknown"

#     batch_data.append((lang, review_id))

#     # Mise à jour par batch
#     if len(batch_data) >= batch_size:
#         cur.executemany("""
#             UPDATE transactional.clean_reviews
#             SET language = %s
#             WHERE id = %s;
#         """, batch_data)
#         conn.commit()
#         batch_data = []  # Réinitialiser le batch

# # Mettre à jour les données restantes
# if batch_data:
#     cur.executemany("""
#         UPDATE transactional.clean_reviews
#         SET language = %s
#         WHERE id = %s;
#     """, batch_data)
#     conn.commit()

# cur.close()
# conn.close()
# print("✅ Mise à jour de la colonne 'language' terminée avec succès ! 🚀")



 
        

from langdetect import detect
import psycopg2
from connect_to_db import connect_to_aiven_db



# Connexion à PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
conn = connect_to_aiven_db()  # Utiliser la fonction de connexion définie dans connect_to_db.py
if not conn:
    raise Exception("Échec de la connexion à la base de données.")

cur = conn.cursor()
print("✅ Connexion réussie à la base de données.")

# Vérifier si la colonne 'language' existe dans la table cible
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'clean_reviews'
          AND column_name = 'language'
    );
""")
language_column_exists = cur.fetchone()[0]

# Ajouter la colonne 'language' si elle n'existe pas
if not language_column_exists:
    cur.execute("""
        ALTER TABLE transactional.clean_reviews
        ADD COLUMN language TEXT;
    """)
    conn.commit()
    print("✅ Colonne 'language' ajoutée à la table 'clean_reviews'.")

# Récupérer les avis où la colonne 'language' est NULL ou non définie
cur.execute("""
    SELECT id, review_text
    FROM transactional.clean_reviews
    WHERE language IS NULL OR language = '' OR language = 'unknown';
""")
rows = cur.fetchall()

batch_size = 500  # Taille du batch pour optimiser les mises à jour
batch_data = []

# Détection de la langue et préparation des données pour la mise à jour
for row in rows:
    review_id, text = row

    
    try:
        lang = detect(text)
    except:
        lang = "unknown"

    batch_data.append((lang, review_id))

    # Mise à jour par batch
    if len(batch_data) >= batch_size:
        cur.executemany("""
            UPDATE transactional.clean_reviews
            SET language = %s
            WHERE id = %s;
        """, batch_data)
        conn.commit()
        batch_data = []  # Réinitialiser le batch

# Mettre à jour les données restantes
if batch_data:
    cur.executemany("""
        UPDATE transactional.clean_reviews
        SET language = %s
        WHERE id = %s;
    """, batch_data)
    conn.commit()

cur.close()
conn.close()
print("✅ Mise à jour de la colonne 'language' terminée avec succès ! 🚀")