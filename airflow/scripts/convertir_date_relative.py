import psycopg2
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from connect_to_db import connect_to_aiven_db

# 🔹 Fonction pour convertir une date relative en date absolue
def convertir_date_relative(date_relative):
    """
    Convertit une date relative (ex: 'il y a 10 mois', 'il y a un jour') en date absolue au format YYYY/MM/DD.
    Si la date est NULL ou invalide, retourne "Date inconnue".
    """
    if not date_relative or date_relative.strip().lower() == "null":
        return None

    # Définir la date actuelle (aujourd'hui)
    aujourd_hui = datetime.today()

    # Normaliser la chaîne pour supprimer les espaces insécables (` `)
    date_relative = date_relative.replace(" ", " ")

    # Utiliser une expression régulière pour extraire le nombre et l'unité (mois, ans, an, jour)
    match = re.search(r"il y a (\d+)( mois| ans| an| jours| jour| semaines| semaine)", date_relative)
    
    if match:
        nombre = int(match.group(1))
        unite = match.group(2).strip()
        
        # Calculer la date en fonction de l'unité
        if unite == "mois":
            nouvelle_date = aujourd_hui - relativedelta(months=nombre)
        elif unite == "an" or unite == "ans":
            nouvelle_date = aujourd_hui - relativedelta(years=nombre)
        elif unite == "jour" or unite == "jours":
            nouvelle_date = aujourd_hui - relativedelta(days=nombre)
        elif unite == "semaine" or unite == "semaines":
            nouvelle_date = aujourd_hui - timedelta(weeks=nombre)  # 1 semaine = 7 jours

        return nouvelle_date.strftime("%Y-%m-%d")  # Format YYYY/MM/DD
    
    # Cas particulier : "il y a un an"
    if date_relative.strip() == "il y a un an":
        nouvelle_date = aujourd_hui - relativedelta(years=1)
        return nouvelle_date.strftime("%Y/%m/%d")

    # Cas particulier : "il y a un mois"
    if date_relative.strip() == "il y a un mois":
        nouvelle_date = aujourd_hui - relativedelta(months=1)
        return nouvelle_date.strftime("%Y/%m/%d")

    # Cas particulier : "il y a un jour"
    if date_relative.strip() == "il y a un jour":
        nouvelle_date = aujourd_hui - relativedelta(days=1)
        return nouvelle_date.strftime("%Y/%m/%d")
        # Cas particulier : "il y a une semaine"
    if date_relative.strip() == "il y a une semaine":
        nouvelle_date = aujourd_hui - timedelta(weeks=1)  # 1 semaine = 7 jours
        return nouvelle_date.strftime("%Y/%m/%d")

    # Si aucune correspondance n'est trouvée
    return None

# 🔹 Connexion à PostgreSQL
try:

    conn = connect_to_aiven_db()  # Utiliser la fonction de connexion définie dans connect_to_db.py
    if not conn:
        raise Exception("Échec de la connexion à la base de données.")
    
    cur = conn.cursor()
    print("✅ Connexion réussie à la base de données.")

    # 🔹 Création de la table clean_reviews si elle n'existe pas
    # Vérifier si la colonne 'language' existe dans la table cible
    cur.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'clean_reviews'
            AND column_name = 'review_date_absolute'
        );
    """)
    language_column_exists = cur.fetchone()[0]

    # Ajouter la colonne 'language' si elle n'existe pas
    if not language_column_exists:
        cur.execute("""
            ALTER TABLE transactional.clean_reviews
            ADD COLUMN review_date_absolute date;
        """)
        conn.commit()
        print("✅ Colonne 'review_date_absolute' ajoutée à la table 'clean_reviews'.")


    # 🔹 Récupérer les données depuis la table source
    cur.execute("""
        SELECT id, bank_name, branch_name, location, review_text, clean_review, rating, review_date, data_extraction_date
        FROM transactional.clean_reviews;
    """)
    rows = cur.fetchall()

    # 🔹 Insérer ou mettre à jour les données dans la table cible
    for row in rows:
        review_id, bank_name, branch_name, location, review_text, clean_review, rating, review_date, data_extraction_date = row

        # Gérer les valeurs NULL pour review_date
        if not review_date or review_date.strip().lower() == "null":
            review_date = "Date inconnue"

        # Convertir la date relative en date absolue
        date_absolute = convertir_date_relative(review_date)

        # Vérifier si l'ID existe déjà dans la table cible
        cur.execute("""
            SELECT id FROM transactional.clean_reviews WHERE id = %s;
        """, (review_id,))
        existing_record = cur.fetchone()

        if existing_record:
            # Mettre à jour uniquement la colonne review_date_absolute
            cur.execute("""
                UPDATE transactional.clean_reviews
                SET review_date_absolute = %s
                WHERE id = %s;
            """, (date_absolute, review_id))
        else:
            # Insérer une nouvelle ligne dans la table cible
            cur.execute("""
                INSERT INTO transactional.clean_reviews (
                    id, bank_name, branch_name, location, review_text, clean_review, rating, review_date, data_extraction_date, review_date_absolute
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                review_id, bank_name, branch_name, location, review_text, clean_review, rating, review_date, data_extraction_date, date_absolute
            ))

    conn.commit()
    print("✅ Conversion des dates et insertion/mise à jour terminées avec succès.")

except Exception as e:
    print(f"❌ Erreur : {e}")

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()