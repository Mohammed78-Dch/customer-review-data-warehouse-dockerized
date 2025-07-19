import json
from scraper import scrape_bank_reviews  # Importer la fonction de scraping
from scraper_banks import extraire_banques
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 📌 Fonction pour scraper et stocker les données en JSON
def insert_data_to_json(**kwargs):
    try:
        # Appeler la fonction de scraping
        extraire_banques()
        logging.info("✅ Banques extraites avec succès.")
        scrape_bank_reviews()
        logging.info("✅ Données de scraping enregistrées en JSON.")

    except Exception as e:
        logging.info(f"❌ Erreur lors du scraping : {e}")
