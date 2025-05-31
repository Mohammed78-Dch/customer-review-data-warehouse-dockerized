# Analyzing Customer Reviews of Bank Agencies in Morocco

## 1. Project Objective

This project focuses on building a data pipeline to collect, process, and analyze Google Maps reviews for bank agencies in Morocco. The main goal is to extract valuable insights, such as customer sentiment trends and common feedback topics, using a modern data stack. This involves automating the extraction of unstructured review data, cleaning and transforming it, storing it efficiently, and visualizing the results for analysis.

## 2. Tech Stack Used

*   **Data Collection:** Python (with libraries like `requests`, `BeautifulSoup`, or Google Maps API client)
*   **Scheduling:** Apache Airflow
*   **Data Storage:** PostgreSQL
*   **Transformation:** DBT (Data Build Tool)
*   **BI / Visualization:** Google Looker Studio
*   **Version Control:** Git / GitHub

## 3. Project Structure

The project files are organized into the following main directories:

*   `1_data_collection`: Contains the Python script (`google_maps_scraper.py`) and its dependencies (`requirements.txt`) for fetching reviews.
*   `2_airflow_automation`: Holds the Airflow DAGs (`data_collection_dag.py`, `data_pipeline_dag.py`) that automate the pipeline execution.
*   `3_dbt_transformation`: The DBT project folder where data cleaning, transformation, and modeling logic resides (within `models/`). Includes `dbt_project.yml` for configuration.
*   `4_database_setup`: Contains the `schema_creation.sql` script to set up the necessary tables in your PostgreSQL database.
*   `5_looker_dashboard`: Includes `dashboard_info.txt` with the link to the final Looker Studio dashboard.

## 4. Setup Instructions

1.  **Clone Repository:** Get the code: `git clone <repository_url>` and `cd project_root`.
2.  **Python Environment (Data Collection):** Go to `1_data_collection`, create a virtual environment (`python -m venv venv`), activate it (`source venv/bin/activate`), and install requirements (`pip install -r requirements.txt`). Configure any necessary API keys or settings.
3.  **PostgreSQL:** Ensure PostgreSQL is running. Create a database for this project. Run the script in `4_database_setup/schema_creation.sql` to create the tables.
4.  **DBT:** Go to `3_dbt_transformation`, set up a Python virtual environment if needed (`pip install dbt-postgres`), and configure your `profiles.yml` (usually in `~/.dbt/` or see DBT docs) with your PostgreSQL connection details. Make sure this profile is referenced in `dbt_project.yml`.
5.  **Airflow:** Install and configure Apache Airflow. Set up a PostgreSQL connection in Airflow. Place the DAG files from `2_airflow_automation` into your Airflow DAGs folder.

## 5. How to Run the Pipeline

1.  **Airflow:** The primary way to run the pipeline is through Airflow. Ensure Airflow is running and the DAGs (`data_collection_dag.py`, `data_pipeline_dag.py`) are active. Trigger the main pipeline DAG (`data_pipeline_dag.py`) manually for the first run or rely on its schedule.
2.  **Manual Steps (Optional):**
    *   Run the data collection script in `1_data_collection` manually.
    *   Run DBT commands from within the `3_dbt_transformation` directory (`dbt run`, `dbt test`) after data is collected.

## 6. Deliverables Location

*   **Data Collection Script:** `1_data_collection/google_maps_scraper.py`
*   **Airflow DAGs:** `2_airflow_automation/`
*   **DBT Models:** `3_dbt_transformation/models/`
*   **PostgreSQL Schema Script:** `4_database_setup/schema_creation.sql`
*   **Looker Studio Dashboard:** Link in `5_looker_dashboard/dashboard_info.txt`
*   **Project Documentation:** This `README.md` file.

## 7. Dashboard Access

The final analysis and visualizations are available on a Google Looker Studio dashboard. Please find the access link in the `5_looker_dashboard/dashboard_info.txt` file.

## 8. License

[Specify License, e.g., MIT License]

## 9. Authors

*  Mohammed Dechraoui
   Master 2 Systèmes d'Information et Systèmes Intelligents (M2SI)
   Institut National de Statistique et d'Économie Appliquée (INSEA)
