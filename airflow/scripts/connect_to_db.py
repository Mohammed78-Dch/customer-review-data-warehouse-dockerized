# import psycopg2

# def connect_to_aiven_db():
#     try:
#         conn = psycopg2.connect(
#             # dbname="project_data_wherhouse",
#             # user="avnadmin",
#             # password="AVNS_Mog690hTB5WdacVAvzF",  # 🔒 Remplace avec ton mot de passe réel
#             # host="pg-365fb9de-mmohxx20-ac9b.j.aivencloud.com",
#             # port="15054",
#             # sslmode="require"  # 🔐 Obligatoire pour Aiven
#             dbname="airflow",
#             user="airflow",
#             password="airflow",
#             host="postgres",
#             port="5432"
#             # sslmode="require"  # 🔐 Obligatoire pour Aiven
#         )
#         print("✅ Connexion réussie à la base de données Aiven PostgreSQL.")
#         return conn
#     except Exception as e:
#         print(f"❌ Échec de la connexion : {e}")
#         return None



import psycopg2
import logging
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException
import os

def connect_to_aiven_db(conn_id='postgres_default'):
    """
    Connect to a PostgreSQL database and initialize the schema for all_bank_reviews.
    
    Args:
        conn_id (str): Airflow Connection ID for the PostgreSQL database (default: 'postgres_default').
    
    Returns:
        psycopg2.connection: Database connection object.
    
    Raises:
        AirflowException: If connection or schema initialization fails.
    """
    try:
        # Get connection details from Airflow Connection
        conn = BaseHook.get_connection(conn_id)
        
        # Fallback to environment variables if connection not found
        db_params = {
            'dbname': conn.schema or os.getenv('PG_DBNAME', 'airflow'),
            'user': conn.login or os.getenv('PG_USER', 'airflow'),
            'password': conn.password or os.getenv('PG_PASSWORD', 'airflow'),
            'host': conn.host or os.getenv('PG_HOST', 'postgres'),
            'port': conn.port or os.getenv('PG_PORT', '5432'),
            'sslmode': conn.extra_dejson.get('sslmode', 'require') if conn.host and conn.host.endswith('aivencloud.com') else 'prefer'
        }

        # Establish connection
        connection = psycopg2.connect(**db_params)
        connection.autocommit = True  # Enable autocommit for schema creation
        logging.info("✅ Connexion réussie à la base de données PostgreSQL: %s", db_params['dbname'])

        # Initialize schema (sequence and table)
        with connection.cursor() as cursor:
            # Create sequence
            cursor.execute("""
                CREATE SEQUENCE IF NOT EXISTS bank_reviews_id_seq
                    INCREMENT 1
                    START 1
                    MINVALUE 1
                    MAXVALUE 2147483647
                    CACHE 1;
            """)
            logging.info("✅ Séquence bank_reviews_id_seq vérifiée/créée")

            # Create table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.all_bank_reviews (
                    id INTEGER NOT NULL DEFAULT nextval('bank_reviews_id_seq'::regclass),
                    bank_name TEXT COLLATE pg_catalog."default" NOT NULL,
                    branch_name TEXT COLLATE pg_catalog."default" NOT NULL,
                    location TEXT COLLATE pg_catalog."default" NOT NULL,
                    review_text TEXT COLLATE pg_catalog."default",
                    rating DOUBLE PRECISION,
                    review_date TEXT NOT NULL,
                    data_extraction_date DATE DEFAULT CURRENT_DATE,
                    CONSTRAINT bank_reviews_pkey PRIMARY KEY (id),
                    CONSTRAINT unique_review UNIQUE (location, review_date, review_text)
                );
            """)
            logging.info("✅ Table public.all_bank_reviews vérifiée/créée")

            # Set sequence ownership
            cursor.execute("""
                ALTER SEQUENCE bank_reviews_id_seq OWNED BY public.all_bank_reviews.id;
            """)
            logging.info("✅ Séquence bank_reviews_id_seq associée à la table")

            # Sync sequence with existing data
            cursor.execute("""
                SELECT setval('bank_reviews_id_seq', COALESCE((SELECT MAX(id) + 1 FROM public.all_bank_reviews), 1));
            """)
            logging.info("✅ Séquence bank_reviews_id_seq synchronisée avec les données existantes")

            # Verify table existence
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'all_bank_reviews'
                );
            """)
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                logging.error("❌ Échec de la création de la table public.all_bank_reviews")
                raise AirflowException("Failed to create table public.all_bank_reviews")

        return connection
    except psycopg2.Error as e:
        logging.error("❌ Échec de la connexion ou de l'initialisation du schéma : %s", e)
        raise AirflowException(f"Database error: {e}")
    except Exception as e:
        logging.error("❌ Erreur inattendue : %s", e)
        raise AirflowException(f"Unexpected error: {e}")