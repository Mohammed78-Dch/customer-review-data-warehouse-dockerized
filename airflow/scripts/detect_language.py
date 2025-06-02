
        

from langdetect import detect
from connect_to_db import connect_to_aiven_db



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