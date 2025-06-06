from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import re
import random
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import quote_plus
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
banks_maroc_path = os.path.join(base_dir, "banks_maroc.json")
banks_maroc_err_path = os.path.join(base_dir, "banks_maroc_ERR.json")
# Configuration Chrome (2024)
# service = Service(ChromeDriverManager().install())
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# # options.add_argument("--headless=new")  # Uncomment for headless mode

# driver = webdriver.Chrome(options=options)
# driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Banks list
banks = [
    "Bank Al-Maghrib",
    "Attijariwafa Bank",
    "Banque Populaire",
    "Bank of Africa",
    "BMCE Bank",
    "Crédit du Maroc",
    "Société Générale Maroc",
    "BMCI",
    "CFG Bank",
    "CIH Bank",
    "Crédit Agricole du Maroc",
    "Al Barid Bank",
    "Arab Bank Maroc",
    "Citibank Morocco",
    "Union Marocaine de Banques",
    "Umnia Bank",
    "Bank Al Yousr",
    "BTI Bank",
    "Al Akhdar Bank",
    "Bank Assafa",
    "CDG Capital",
    "Attijari Finances Corp.",
    "BMCE Capital",
    "Upline Group",
    "Casablanca Finance Group",
    "Attijari International Bank",
    "Banque Internationale de Tanger",
    "BMCI - Banque Offshore",
    "Chaabi International Bank",
    "Société Générale Banque Offshore",
    "BMCE Offshore"
]

banques = []
doublons = set()

# Extended bank names list (French/Arabic/English)
main_banks = [
    "Bank Al-Maghrib", "بنك المغرب",
    "Attijariwafa Bank", "التجاري وفا بنك",
    "Banque Populaire", "البنك الشعبي",
    "Bank of Africa", "بنك أفريقيا",
    "BMCE Bank", "بنك BMCE",
    "Crédit du Maroc", "القرض العقاري",
    "Société Générale Maroc", "البنك العام المغربي",
    "BMCI", "بنك BMCI",
    "CFG Bank", "CFG بنك",
    "CIH Bank", "بنك CIH",
    "Crédit Agricole du Maroc", "القرض الفلاحي للمغرب",
    "Al Barid Bank", "البريد بنك",
    "Arab Bank Maroc", "البنك العربي المغربي",
    "Citibank Morocco", "سيتي بنك المغرب",
    "Union Marocaine de Banques", "الاتحاد المغربي للبنوك",
    "Umnia Bank", "بنك أمين",
    "Bank Al Yousr", "بنك اليسر",
    "BTI Bank", "بنك BTI",
    "Al Akhdar Bank", "البنك الأخضر",
    "Bank Assafa", "بنك الصفاء",
    "CDG Capital", "CDG كابيتال",
    "Attijari Finances Corp.", "التجاري للتمويل",
    "BMCE Capital", "BMCE كابيتال",
    "Upline Group", "مجموعة أوبلاين",
    "Casablanca Finance Group", "مجموعة الدار البيضاء المالية",
    "Attijari International Bank", "التجاري بنك الدولي",
    "Banque Internationale de Tanger", "البنك الدولي لطنجة",
    "BMCI - Banque Offshore", "BMCI - البنك الخارجي",
    "Chaabi International Bank", "الشعبي بنك الدولي",
    "Société Générale Banque Offshore", "البنك العام الخارجي",
    "BMCE Offshore", "BMCE البنك الخارجي"
]

villes = [
    "Casablanca","Rabat","Fès", "Marrakech", "Tanger", "Agadir", "Meknès", "Oujda",
    "Tétouan", "Nador", "Kénitra", "Safi", "El Jadida", "Beni Mellal", "Taza",
    "Khouribga", "Ouarzazate", "Mohammedia", "Berkane", "Errachidia", "Guelmim",
    "Laâyoune", "Dakhla", "Settat", "Larache", "Al Hoceïma", "Khémisset",
    "Taourirt", "Fkih Ben Salah", "Taroudant", "Azrou", "Ifrane", "Benslimane",
    "Tan-Tan", "Tinghir", "Tiznit", "Midelt", "Sidi Kacem", "Sidi Slimane",
    "Sidi Bennour", "Youssoufia", "Boujdour", "Smara", "Jerada", "Demnate",
    "Azilal", "Aït Melloul", "Skhirat", "Temara", "Martil", "Fnideq",
    "Souk El Arbaa", "Zagora", "Akhfenir", "Assilah", "Chefchaouen", "Ouazzane",
    "Ksar El Kebir", "Bir Jdid", "Imzouren", "Ait Baha", "Sefrou", "Boulemane",
    "Missour", "Guercif", "Oued Zem", "Ait Ourir", "Kalaat Sraghna", "Tahanaout"
]

def extraire_infos_agence(nom_complet, main_banks, adresse_de_bank):
    nom_clean = nom_complet.lower()
        # Nettoyage de l'adresse : enlever ., ,, *
    adresse_de_bank = re.sub(r"[.,*]", "", adresse_de_bank).strip()
    # Étape 1 : Détection du nom de la banque
    bank_name = None
    for bank in main_banks:
        if bank.lower() in nom_clean:
            bank_name = bank
            break
    if not bank_name:
        words_nom = set(nom_clean.split())
        best_match = None
        max_common = 0
        for bank in main_banks:
            bank_words = set(bank.lower().split())
            common = words_nom.intersection(bank_words)
            if len(common) > max_common:
                best_match = bank
                max_common = len(common)
        bank_name = best_match if best_match else "Banque inconnue"

    # Étape 2 : Vérifier s’il y a une "adresse" significative dans nom_complet
    # On considère qu’il y a une adresse si des mots comme "rue", "avenue", "hay", "quartier", etc. sont présents
    adresse_keywords = ["rue", "avenue", "hay", "quartier", "bd", "lot", "immeuble", "residence", "n°", "numero"]
    contient_adresse = any(keyword in nom_clean for keyword in adresse_keywords)

    if contient_adresse:
        agency_name = nom_complet.strip()
    else:
        agency_name = f"agence {bank_name} {adresse_de_bank}".strip()

    return bank_name, agency_name


def contient_mot_cle(nom_complet):
    """Check if the name contains keywords that should be filtered out"""
    mots_cles_exclusion = [
        "atm", "distributeur", "guichet", "change", "bureau", "poste", 
        "pharmacy", "pharmacie", "restaurant", "hotel", "cafe"
    ]
    nom_lower = nom_complet.lower()
    return any(mot in nom_lower for mot in mots_cles_exclusion)


def extraire_note_adresse(text):
    """Extract rating from address/note text"""
    match = re.search(r'(\d+\.?\d*)\s*étoiles?', text)
    if match:
        return match.group(1)
    
    match = re.search(r'(\d+,\d+)', text)
    if match:
        return match.group(1).replace(',', '.')
        
    return "N/A"

def scroll_pour_charger_tout(driver, conteneur):
    """Scroll to load all results"""
    last_height = 0
    retries = 0
    
    while retries < 20:
        driver.execute_script("arguments[0].scrollBy(0, 500)", conteneur)
        time.sleep(random.uniform(2, 3))
        
        new_height = driver.execute_script("return arguments[0].scrollHeight", conteneur)
        if new_height == last_height:
            retries += 1
        else:
            retries = 0
            
        last_height = new_height
    
    print("✅ Fin du scrolling")
   
   
def setup_driver(profile_name="SeleniumProfile", headless=False):
    """Configure WebDriver with a custom profile for extensions."""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # Créer un profil personnalisé
    profile_path = os.path.expanduser("~") + f"/ChromeProfiles/{profile_name}"
    os.makedirs(profile_path, exist_ok=True)
    
    
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--profile-directory=Default")
    
    # Options anti-détection
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
    options.add_argument("--lang=fr,en;q=0.9,ar;q=0.8")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # if headless:
    #     options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver 


def extraire_banques():
    driver = setup_driver(headless=True)

    for ville in villes:
        print(f"\n📍 Initialisation pour {ville}...")
        search_query = f"banques {ville} Maroc"
        encoded_query = quote_plus(search_query)
        driver.get(f"https://www.google.com/maps/search/{encoded_query}")
        
        try:
            # Handle CAPTCHA
            if "captcha" in driver.current_url.lower():
                input("⚠️ CAPTCHA détecté ! Résoudre manuellement puis appuyer sur Entrée...")
            
            # Wait for results with universal selector
            conteneur_avis = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
            )
            
            # Scroll to load all results
            scroll_pour_charger_tout(driver, conteneur_avis)
            
            # Extract all results
            resultats = driver.find_elements(By.XPATH, "//div[starts-with(@class, 'Nv2PK')]")
            print(f"[{ville}] {len(resultats)} résultats trouvés")
            count = 0
            
            for resultat in resultats:
                try:
                    # Extract full name
                    try:
                        nom_complet = resultat.find_element(By.XPATH, ".//div[contains(@class, 'qBF1Pd') and contains(@class, 'fontHeadlineSmall')]").text
                    except:
                        try:
                            nom_complet = resultat.get_attribute("aria-label") or "N/A"
                        except:
                            continue
                    
                    # Skip if contains excluded keywords
                    if contient_mot_cle(nom_complet):
                        continue
                    
                    
                    
                    

                    try:
                        # Première classe W4Efsd (adresse)
                        adresse_elements = resultat.find_element(By.XPATH, ".//div[@class='W4Efsd'][2]").text.split('·')[1].strip().split('\n')[0]
                        if adresse_elements =="": adresse = resultat.find_element(By.XPATH, ".//div[@class='W4Efsd'][2]").text.split('·')[2].strip().split('\n')[0]
                        else:
                            adresse = adresse_elements
                    except:
                        adresse_elements = "N/A"
                    # Extract phone
                    try:
                        telephone = resultat.find_element(By.XPATH, ".//span[@class='UsdlK']").text.strip()
                    except:
                        telephone = "N/A"
                    
                    # Extract rating
                    try:
                        raw_text = resultat.find_element(By.XPATH, ".//div[contains(@class, 'W4Efsd')]").text
                        note = extraire_note_adresse(raw_text)
                    except:
                        note = "N/A"
                    
                    # Extract branch name
                    bank_name, agence = extraire_infos_agence(nom_complet, main_banks, adresse)
                    
                    # Extract URL
                    url = "N/A"
                    try:
                        url = resultat.find_element(By.XPATH, ".//a").get_attribute("href")
                    except:
                        try:
                            url = resultat.find_element(By.XPATH, ".//button").get_attribute("data-href")
                        except:
                            pass
                    
                    # Extract Google Maps place ID
                    place_id = None
                    if url and "place" in url:
                        match = re.search(r"place/([^/?]+)", url)
                        if match:
                            place_id = match.group(1)

                    # Check for duplicates and valid URL
                    if url and url not in doublons and url != "N/A" and bank_name != "Banque inconnue":
                        banque_data = {
                            "id": place_id,
                            "Bank name": bank_name,
                            "branch name": agence,
                            "url": url,
                            "Bank rating": note,
                            "location": adresse,
                            "telephone": telephone,
                            "city": ville,
                            "slug": re.sub(r'[^a-z0-9\u0600-\u06FF]+', '-', nom_complet.lower()),
                        }
                        
                        banques.append(banque_data)
                        doublons.add(url)
                        count += 1
                        
                        print(f"✅ {nom_complet} ({agence})")
                    else:
                        print(f"🚫 Doublon ou données incomplètes : {nom_complet}")
                        
                except Exception as e:
                    print(f"⚠️ Élément non parsé : {str(e)[:50]}")
                    continue
                    
            print(f"[{ville}] {count} banques enregistrées" if count > 0 else f"[{ville}] Aucune banque enregistrée")
            print(f"✅ [{ville}] Extraction terminée")
            
        except Exception as e:
            print(f"❌ [{ville}] Erreur critique : {str(e)[:100]}")
            driver.save_screenshot(f"erreur_{ville}.png")
        
        # Add delay between cities to avoid rate limiting
        time.sleep(random.uniform(0.5, 1))
        
    # Charger les banques existantes (si le fichier existe)
    if os.path.exists(banks_maroc_path):
        with open(banks_maroc_path, "r", encoding="utf-8") as f:
            banques_existantes = json.load(f)
    else:
        banques_existantes = []

    # Obtenir les URLs déjà enregistrées
    urls_existantes = {bank['url'] for bank in banques_existantes}

    # Nouvelle liste pour stocker les banques extraites
    banques_nouvelles = []

    # Execute scraping
    try:
        extraire_banques()  # Cette fonction remplit une variable `banques`, supposée globale

        for bank in banques:
            if bank['url'] not in urls_existantes:
                banques_nouvelles.append(bank)
                urls_existantes.add(bank['url'])  # Éviter les doublons si répétées dans la même session
            else:
                print(f"⏭️ Banque déjà présente (URL existante) : {bank['Bank name']}")

        # Ajouter les nouvelles banques à l’ensemble existant
        banques_total = banques_existantes + banques_nouvelles

        # Sauvegarder le tout
        with open(banks_maroc_path, "w", encoding="utf-8") as f:
            json.dump(banques_total, f, indent=4, ensure_ascii=False)

        print(f"\n🌟 Extraction terminée : {len(banques_nouvelles)} nouvelles banques ajoutées")
        print(f"📁 Total banques enregistrées : {len(banques_total)} dans 'banks_maroc.json'")

    except KeyboardInterrupt:
        print("\n⚠️ Arrêt forcé par l'utilisateur")

    except Exception as e:
        print(f"\n❌ Erreur critique : {str(e)}")

    finally:
        # Sauvegarde partielle en cas d'erreur
        if banques_nouvelles:
            with open(banks_maroc_err_path, "w", encoding="utf-8") as f:
                json.dump(banques_nouvelles, f, indent=4, ensure_ascii=False)
            print(f"💾 Sauvegarde partielle : {len(banques_nouvelles)} nouvelles banques")

        try:
            driver.quit()
            print("🔚 WebDriver fermé")
        except Exception:
            print("🔚 WebDriver déjà fermé ou non initialisé")
