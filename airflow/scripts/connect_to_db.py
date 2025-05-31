import psycopg2

def connect_to_aiven_db():
    try:
        conn = psycopg2.connect(
            dbname="project_data_wherhouse",
            user="avnadmin",
            password="AVNS_Mog690hTB5WdacVAvzF",  # 🔒 Remplace avec ton mot de passe réel
            host="pg-365fb9de-mmohxx20-ac9b.j.aivencloud.com",
            port="15054",
            sslmode="require"  # 🔐 Obligatoire pour Aiven
        )
        print("✅ Connexion réussie à la base de données Aiven PostgreSQL.")
        return conn
    except Exception as e:
        print(f"❌ Échec de la connexion : {e}")
        return None
