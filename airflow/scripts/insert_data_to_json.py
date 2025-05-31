import json
from scraper import scrape_bank_reviews  # Importer la fonction de scraping
from scraper_banks import extraire_banques


# 📌 Fonction pour scraper et stocker les données en JSON
def insert_data_to_json(**kwargs):
    try:
        # Appeler la fonction de scraping
        extraire_banques()
        print("✅ Banques extraites avec succès.")
        scrape_bank_reviews()
        print("✅ Données de scraping enregistrées en JSON.")

    except Exception as e:
        print(f"❌ Erreur lors du scraping : {e}")
