from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import os
# import sys

# # 👉 Calcul du chemin absolu vers le dossier scripts/
# current_dir = os.path.dirname(os.path.abspath(__file__))  # chemin du fichier DAG
# scripts_path = os.path.abspath(os.path.join(current_dir, '..', 'scripts'))
# sys.path.append(scripts_path)
# # Ajoute ça en haut (juste après scripts_path)
# project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))  # Racine du projet
# dbt_transactional_path = os.path.join(project_root, '.dbt', 'dbt_projects', 'bank_reviews_transactional')
# dbt_decisionnal_path = os.path.join(project_root, '.dbt', 'dbt_projects', 'bank_reviews_decisionnal')

# # 👉 Importation des fonctions Python personnalisées
# from scripts.insert_data_to_postgresql import insert_data_to_postgresql
# from scripts.insert_data_to_json import insert_data_to_json

import sys

# Chemin absolu vers le dossier du fichier DAG
current_dir = os.path.dirname(os.path.abspath(__file__))

# Ajouter le dossier scripts au path pour importer les modules
scripts_path = os.path.abspath(os.path.join(current_dir, '..', 'scripts'))
sys.path.append(scripts_path)

# Optionnel : ajouter la racine du projet et dossiers dbt si besoin
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
dbt_transactional_path = os.path.join(project_root, '.dbt', 'dbt_projects', 'bank_reviews_transactional')
dbt_decisionnal_path = os.path.join(project_root, '.dbt', 'dbt_projects', 'bank_reviews_decisionnal')

sys.path.append(dbt_transactional_path)
sys.path.append(dbt_decisionnal_path)

# Maintenant, tu peux importer tes modules scripts
from insert_data_to_postgresql import insert_data_to_postgresql
from insert_data_to_json import insert_data_to_json

# Ton code DAG ici...


default_args = {
    'owner': 'mohammed',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 8),
    'retries': 0,
}

dag = DAG(
    'bank_reviews_etl_and_analysis_pipeline',
    default_args=default_args,
    description='Pipeline ETL et analyse des avis bancaires avec DBT, détection de langue, analyse de sentiment et modélisation de thèmes.',
    schedule_interval='@weekly',
)

# Tâche pour insérer les données en JSON
scraping_insert_task_json = PythonOperator(
    task_id='scrape_and_insert_data_to_json',
    python_callable=insert_data_to_json,
    provide_context=True,
    dag=dag,
)

insert_task_dataBase = PythonOperator(
    task_id='insert_data_to_postgresql',
    python_callable=insert_data_to_postgresql,
    provide_context=True,
    dag=dag,
)

dbt_run_transactional = BashOperator(
    task_id='dbt_run_transactional',
    bash_command=f'cd {dbt_transactional_path} && dbt run',
    dag=dag,
)


detect_language = BashOperator(
    task_id="detect_language",
    bash_command=f"python3 {scripts_path}/detect_language.py",
    dag=dag,
)

sentiment_analysis = BashOperator(
    task_id="sentiment_analysis",
    bash_command=f"python3 {scripts_path}/sentiment_analysis.py",
    dag=dag,
)

topic_modeling = BashOperator(
    task_id="topic_modeling",
    bash_command=f"python3 {scripts_path}/topic_modeling.py",
    dag=dag,
)

convertir_date_relative = BashOperator(
    task_id="convertir_date_relative",
    bash_command=f"python3 {scripts_path}/convertir_date_relative.py",
    dag=dag,
)

dbt_run_decisionnal = BashOperator(
    task_id='dbt_run_decisionnal',
    bash_command=f'cd {dbt_decisionnal_path} && dbt run --full-refresh',
    dag=dag,
)

# Définition de l'ordre des tâches
scraping_insert_task_json >> insert_task_dataBase >> dbt_run_transactional >> convertir_date_relative >> detect_language >> sentiment_analysis >> topic_modeling >> dbt_run_decisionnal

print("✅ Pipeline ETL et analyse des avis bancaires configuré avec succès.")
