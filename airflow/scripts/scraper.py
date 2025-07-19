"""
Optimized Bank Reviews Scraper
This script extracts Google reviews for Moroccan banks with improved performance.
"""
import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import os
import logging
import tempfile


# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


base_dir = os.path.dirname(os.path.abspath(__file__))  # dossier du script courant

# Construire le chemin relatif sans le répéter
banks_maroc_path = os.path.join(base_dir, 'banks_maroc.json')
avis_path = os.path.join(base_dir, 'avis.json')
logging.info(f"Loading from: {banks_maroc_path}")  # Debug si nécessaire

# Configuration constants
MAX_SCROLL_RETRIES = 5  # Reduced from 10 to 5 for faster execution
SCROLL_WAIT_TIME = (0.5, 1.0)  # Reduced wait time between scrolls
# MAX_BANKS = None  # Set to a number to limit processing, None for all
MAX_BANKS = 2
# def setup_driver(headless=True):
#     """Configure and return a Selenium WebDriver with anti-detection measures."""
#     service = Service(ChromeDriverManager().install())
#     options = webdriver.ChromeOptions()
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
#     options.add_argument("--lang=fr,en;q=0.9,ar;q=0.8")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
    
#     # if headless:
#     #     options.add_argument("--headless=new")
    
#     driver = webdriver.Chrome(service=service, options=options)
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#     return driver


# def setup_driver(profile_name="SeleniumProfile", headless=False):
#     """Configure WebDriver with a custom profile for extensions."""
#     service = Service(ChromeDriverManager().install())
#     options = webdriver.ChromeOptions()
    
#     # Créer un profil personnalisé
#     profile_path = os.path.expanduser("~") + f"/ChromeProfiles/{profile_name}"
#     os.makedirs(profile_path, exist_ok=True)
    
#     options.add_argument(f"--user-data-dir={profile_path}")
#     options.add_argument("--profile-directory=Default")
    
#     # Options anti-détection
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
#     options.add_argument("--lang=fr,en;q=0.9,ar;q=0.8")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
    
#     # if headless:
#     #     options.add_argument("--headless=new")
    
#     driver = webdriver.Chrome(service=service, options=options)
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
#     return driver

def setup_driver(profile_name=None, headless=False):
    """Configure WebDriver with an optional custom profile for extensions."""

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    if profile_name:
        # Crée un profil fixe si on a précisé profile_name
        profile_path = os.path.expanduser("~") + f"/ChromeProfiles/{profile_name}"
        os.makedirs(profile_path, exist_ok=True)
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
    else:
        # Sinon, créer un user-data-dir temporaire unique
        temp_profile_path = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_profile_path}")

    # Options anti-détection
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
    options.add_argument("--lang=fr,en;q=0.9,ar;q=0.8")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def accept_cookies(driver):
    """Accept cookies if the consent dialog appears."""
    try:
        WebDriverWait(driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'consent.google.com')]"))
        )
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accepter')]"))
        ).click()
        driver.switch_to.default_content()
        return True
    except:
        return False

def get_bank_metadata(soup):
    """Extract bank name and location from page metadata."""
    bank_name_meta = soup.find('meta', {'property': 'og:site_name'})
    bank_name = bank_name_meta['content'].split('·')[0].strip() if bank_name_meta else 'N/A'
    
    address_meta = soup.find('meta', {'property': 'og:title'})
    location = address_meta['content'].split('·')[1].strip() if address_meta and '·' in address_meta['content'] else ''
    
    return bank_name, location

# def click_reviews_button(driver):
#     """Click on the reviews button to open the reviews section."""
#     try:
#         reviews_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'avis') or contains(@aria-label, 'الآراء')]"))
#         )
#         reviews_button.click()
#         return True
#     except:
#         return False

def click_reviews_button(driver):
    """Click on the reviews button to open the reviews section."""
    try:
        reviews_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Avis') or contains(@aria-label, 'الآراء')]"))
        )
        reviews_button.click()
        return True
    except:
        return False

def scroll_reviews(driver, container):
    """Scroll through reviews container with optimized retry logic."""
    last_height = 0
    retries = 0
    
    while retries < MAX_SCROLL_RETRIES:
        # Scroll down
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        
        # Randomized wait time (shorter than original)
        time.sleep(random.uniform(*SCROLL_WAIT_TIME))
        
        # Check if we've reached the end
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == last_height:
            retries += 1
        else:
            retries = 0
            
        last_height = new_height
    
    return True

def extract_reviews(driver, soup):
    """Extract review data from the page using BeautifulSoup."""
    reviews = []
    review_blocks = soup.find_all('div', class_='jftiEf')
    elements_avis = driver.find_elements(By.XPATH, "//div[contains(@class, 'jJc9Ad')]")
    
    for element, block in zip(elements_avis, review_blocks):
        try:
            # Expand truncated reviews
            try:
                voir_plus = element.find_element(By.XPATH, ".//button[contains(@aria-label, 'Voir plus') or contains(@aria-label, 'عرض المزيد')]")
                if voir_plus.is_displayed():
                    driver.execute_script("arguments[0].click();", voir_plus)
                    # Reduced wait time
                    time.sleep(0.5)
            except:
                pass
            
            # Extract review data
            texte = block.find('span', class_='wiI7pd').text.strip() if block.find('span', class_='wiI7pd') else ''
            auteur = block.find('div', class_='d4r55').text.strip() if block.find('div', class_='d4r55') else 'Inconnu'
            note_element = block.find('span', class_='kvMYJc')
            note = note_element['aria-label'][0] if note_element and 'aria-label' in note_element.attrs else ''
            date = block.find('span', class_='rsqaWe').text.strip() if block.find('span', class_='rsqaWe') else ''
            
            if texte:
                reviews.append({
                    "auteur": auteur,
                    "rating": note,
                    "date": date,
                    "avis_text": texte
                })
        except Exception as e:
            continue
    
    return reviews

def extraire_avis(driver, url):
    """Extract all reviews for a given bank URL."""
    driver.get(url + "?hl=fr")
    
    # Accept cookies if needed
    accept_cookies(driver)
    # time.sleep(200)
    # Get bank metadata
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    bank_name, location = get_bank_metadata(soup)
    
    # Click on reviews button
    if not click_reviews_button(driver):
        logging.info(f"❌ Could not find reviews button for URL: {url}")
        return [], location, bank_name
    
    # Wait for reviews container
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'm6QErb') and contains(@class, 'DxyBCb')]"))
        )
    except:
        logging.info(f"❌ Could not find reviews container for URL: {url}")
        return [], location, bank_name
    
    # Scroll to load all reviews
    scroll_reviews(driver, container)
    
    # Extract reviews
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = extract_reviews(driver, soup)
    
    logging.info(f"📌 {len(reviews)} reviews found for {bank_name}")
    return reviews, location, bank_name

def filter_new_reviews(new_reviews, existing_reviews):
    """Filter out reviews that already exist in the database."""
    existing_texts = {review['avis_text'] for review in existing_reviews}
    return [review for review in new_reviews if review['avis_text'] not in existing_texts]

def load_existing_reviews():
    """Load existing reviews from the JSON file."""
    if not os.path.exists(avis_path):
        return {}
        
    try:
        with open(avis_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except json.JSONDecodeError:
        logging.info("❌ Invalid JSON in avis.json, initializing empty database")
        return {}

def save_reviews(all_reviews):
    """Save all reviews to the JSON file."""
    with open(avis_path, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, indent=4, ensure_ascii=False)

def scrape_bank_reviews():
    # Load banks data
    try:
        with open(banks_maroc_path, 'r', encoding='utf-8') as f:
            all_banks = json.load(f)
            # all_banks = all_bankss[:1] # For testing, limit to first bank
    except Exception as e:
        logging.info(f"❌ Error loading banks data: {e}")
        return
    
    # Limit number of banks to process if specified
    banks = all_banks[:MAX_BANKS] if MAX_BANKS else all_banks
    
    # Initialize WebDriver
    driver = setup_driver(headless=True)
    
    try:
        # Load existing reviews
        all_reviews = load_existing_reviews()
        
        # Process each bank
        for index, bank in enumerate(banks, 1):
            logging.info(f"\n[{index}/{len(banks)}] Extracting reviews for {bank['Bank name']}...")
            
            try:
                # Extract reviews
                reviews, location, agence_name = extraire_avis(driver, bank['url'])
                bank_name = bank['Bank name']
                # Determine branch name
                branch_name = (
                    bank['Bank name'] + ' - ' + location if bank['branch name'] == "N/A"
                    else bank['branch name']
                )
                
                # Update reviews database
                if bank['url'] in all_reviews:
                    # Bank exists in database, add only new reviews
                    existing_reviews = all_reviews[bank['url']].get("avis", [])
                    new_reviews = filter_new_reviews(reviews, existing_reviews)
                    
                    if new_reviews:
                        all_reviews[bank['url']]["avis"].extend(new_reviews)
                        all_reviews[bank['url']]["nombre_avis"] = len(all_reviews[bank['url']]["avis"])
                        logging.info(f"➕ Added {len(new_reviews)} new reviews for {bank_name}")
                    else:
                        logging.info(f"🔁 No new reviews for {bank_name}")
                else:
                    # New bank, add all reviews
                    all_reviews[bank['url']] = {
                        "Bank name": bank_name,
                        "branch name": branch_name,
                        "agence name": agence_name,
                        "rating": bank.get("Bank rating", "N/A"),
                        "location": location,
                        "avis": reviews,
                        "nombre_avis": len(reviews)
                    }
                    logging.info(f"🆕 Added new bank: {bank_name}")
                
                # Save after each bank to prevent data loss
                save_reviews(all_reviews)
                
            except Exception as e:
                logging.info(f"❌ Error processing {bank['Bank name']}: {e}")
    
    finally:
        # Clean up
        driver.quit()
        logging.info("🔚 WebDriver closed")

