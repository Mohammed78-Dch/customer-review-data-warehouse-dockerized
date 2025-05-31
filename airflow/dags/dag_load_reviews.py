from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import sys
sys.path.append('/home/mohammed/airflow/scripts')
from insert_data_to_postgresql import insert_data_to_postgresql
from insert_data_to_json import insert_data_to_json


default_args = {
    'owner': 'mohammed',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 17),
    'retries': 1,
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
    provide_context=True,  # Permet de récupérer les logs d'Airflow
    dag=dag,
)

insert_task_dataBase = PythonOperator(
    task_id='insert_data_to_postgresql',
    python_callable=insert_data_to_postgresql,
    provide_context=True,  # Permet de récupérer les logs d'Airflow
    dag=dag,
)


dbt_run_transactional = BashOperator(
    task_id='dbt_run_transactional',
    bash_command='cd /home/mohammed/.dbt/dbt_projects/bank_reviews_transactional && dbt run',
    dag=dag,
)


detect_language = BashOperator(
    task_id="detect_language",
    bash_command="python3 /home/mohammed/airflow/scripts/detect_language.py",
    dag=dag,
)

sentiment_analysis = BashOperator(
    task_id="sentiment_analysis",
    bash_command="python3 /home/mohammed/airflow/scripts/sentiment_analysis.py",
    dag=dag,
)

topic_modeling = BashOperator(
    task_id="topic_modeling",
    bash_command="python3 /home/mohammed/airflow/scripts/topic_modeling.py",
    dag=dag,
)

convertir_date_relative = BashOperator(
    task_id="convertir_date_relative",
    bash_command="python3 /home/mohammed/airflow/scripts/convertir_date_relative.py",
    dag=dag,
)


dbt_run_decisionnal = BashOperator(
    task_id='dbt_run_decisionnal',
    bash_command='cd /home/mohammed/.dbt/dbt_projects/bank_reviews_decisionnal && dbt run --full-refresh',
    dag=dag,
)


scraping_insert_task_json >> insert_task_dataBase >> dbt_run_transactional >> convertir_date_relative >>  detect_language >> sentiment_analysis >> topic_modeling >> dbt_run_decisionnal  
print("✅ Pipeline ETL et analyse des avis bancaires configuré avec succès.")
