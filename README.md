# 📦 Data Warehouse Project Submission

## 📌 Title
**Analyzing Customer Reviews of Bank Agencies in Morocco using a Modern Data Stack**

---

## 👨‍💻 Author

**Mohammed Dechraoui**  
Master 2 – Systèmes d'Information et Systèmes Intelligents (M2SI)  
Institut National de Statistique et d'Économie Appliquée (INSEA)  
📧 mohammed.dechraoui@insea.ac.ma *(example)*  
📅 Academic Year: 2024–2025  

---

## ✅ My Contributions

This project was developed individually as part of the Data Warehouse module. All components of the pipeline were implemented, tested, and documented by me.

### 🔹 Phase 1 – Data Collection
- Implemented a Python-based web scraper using **Scrapy** to extract:
  - Bank name
  - Branch location
  - Review text
  - Rating
  - Date of review
- Used **Google Maps search patterns** to locate bank branches in Morocco.
- Exported data to structured **JSON** and imported it into PostgreSQL.
- Designed and scheduled an **Apache Airflow DAG** to automate weekly extraction.

### 🔹 Phase 2 – Data Cleaning & Transformation
- Used **DBT (Data Build Tool)** to:
  - Clean raw review data (remove duplicates, missing values).
  - Normalize and preprocess text (lowercasing, stop words removal).
- Developed Python scripts to:
  - Detect the language of reviews.
  - Apply **sentiment analysis** using TextBlob.
  - Extract common themes using **LDA topic modeling**.
- Logged transformations and documented DBT models.

### 🔹 Phase 3 – Data Modeling (Star Schema)
- Designed and created the following tables in **PostgreSQL**:
  - `fact_reviews`
  - `dim_bank`
  - `dim_branch`
  - `dim_location`
  - `dim_sentiment`
- Used DBT to create SQL models and load data incrementally.
- Ensured referential integrity and optimized queries for BI tools.

### 🔹 Phase 4 – BI & Analytics
- Built a **Looker Studio (Data Studio)** dashboard:
  - Trends of customer sentiment per bank and branch.
  - Top positive/negative themes extracted from reviews.
  - Ranking of bank branches by average sentiment.
  - Interactive filters for location, bank, and date range.

### 🔹 Phase 5 – Deployment & Automation
- Integrated all steps in a single Apache Airflow workflow:
  - Daily DAG: fetch new reviews, update DBT models, refresh schema.
  - Included email alerts for DAG failures.

---

## 📁 Repository Structure

📁 project-data-warehouse/
├── airflow/
│   ├── dags/
│   │   └── review_pipeline_dag.py
│   └── scripts/
│       ├── scraper.py
│       └── sentiment_analysis.py
├── .dbt/
│   ├── models/
│   └── dbt_project.yml
└── README.md

---

## 🧪 Tools & Libraries Used

- **Languages**: Python, SQL
- **Data Collection**: Scrapy, Google Maps search, JSON
- **Transformation**: DBT
- **Analysis**: TextBlob,  NLTK
- **Automation**: Apache Airflow
- **Database**: PostgreSQL
- **Visualization**: Looker Studio
- **Version Control**: GitHub

---

## 📄 Deliverables Checklist

| Deliverable                        | Status     |
|------------------------------------|------------|
| Python script for data collection  | ✅ Complete |
| Airflow DAGs for automation        | ✅ Complete |
| DBT models for transformation      | ✅ Complete |
| PostgreSQL star schema             | ✅ Complete |
| Looker Studio dashboard            | ✅ Complete |
| Project documentation              | ✅ Complete |

---

## 🧠 Learned Skills

- Designing a modern ETL/ELT pipeline with **Airflow and DBT**
- Applying **NLP techniques** (sentiment analysis, topic modeling) to real-world unstructured data
- Modeling a data warehouse using **star schema**
- Building **interactive BI dashboards** for business users
- End-to-end project automation with scheduling and monitoring

---

## 📚 Supervisor

**Professor:** Dr. [Name of Supervisor]  
Course: Data Warehouse & Business Intelligence  
INSEA – Master M2SI

---

## 📌 Remarks

This project simulates a real-world data engineering and analytics challenge in the banking sector, using customer voice data to drive insights.  
All scripts, models, dashboards, and datasets are included in this submission and stored in the GitHub repository.

