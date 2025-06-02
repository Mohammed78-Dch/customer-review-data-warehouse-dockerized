
import pandas as pd
import nltk
from nltk.corpus import stopwords
from gensim.corpora import Dictionary
from gensim.models import LdaModel
import spacy
from langdetect import detect
import logging
import subprocess
from connect_to_db import connect_to_aiven_db

# Configuration des logs
logging.basicConfig(filename='errors.log', level=logging.WARNING)

# Télécharger les ressources NLTK nécessaires
nltk.download('stopwords')

# Charger SpaCy pour différentes langues
spacy_languages = {
    "en": "en_core_web_sm",
    "fr": "fr_core_news_sm",
    "es": "es_core_news_sm",
    "de": "de_core_news_sm",
}
for lang_code, model_name in spacy_languages.items():
    try:
        # Try to load the model
        spacy.load(model_name)
        print(f"✅ SpaCy model '{model_name}' is already installed.")
    except OSError:
        print(f"⬇️ Downloading SpaCy model '{model_name}'...")
        subprocess.run(["python", "-m", "spacy", "download", model_name])
# Liste des langues prises en charge
supported_languages = list(spacy_languages.keys())

# Détection automatique de la langue avec fallback
def detect_language(text):
    try:
        return detect(text)
    except:
        return "fr"  # Langue par défaut en cas d'échec de détection

# Prétraitement du texte en fonction de la langue
def preprocess(text, language="fr"):
    if language not in supported_languages:
        logging.warning(f"⚠️ Langue non prise en charge détectée : {language}. Utilisation du français par défaut.")
        language = "fr"

    nlp = spacy_languages.get(language)
    if not nlp:
        raise ValueError(f"Langue {language} non prise en charge.")

    doc = nlp(text.lower())  # Tokenisation et mise en minuscules
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]  # Lemmatisation et suppression des stopwords
    return tokens

# Extraction des mots-clés pour chaque topic
def extract_topic_keywords(lda_model, dictionary, num_topics):
    topic_keywords = {}
    for topic_id in range(num_topics):
        words = lda_model.show_topic(topic_id, topn=10)  # Récupérer les 10 mots-clés principaux
        keywords = [word for word, _ in words]
        topic_keywords[topic_id] = keywords
    return topic_keywords

# Fonction pour extraire plusieurs significations pour chaque topic
def extract_topic_meanings(topic_words):
    topic_descriptions = {}

    for topic_id, top_words in topic_words.items():
        meanings = []

        if any(word in top_words for word in ["service", "bon", "avis", "accompagner"]):
            meanings.append("Qualité du service et relation client")
        if any(word in top_words for word in ["frais", "carte", "guichet", "plus"]):
            meanings.append("Frais bancaires et gestion des comptes")
        if any(word in top_words for word in ["dattente", "minutes", "agent", "sécurité"]):
            meanings.append("Temps d'attente et gestion en agence")
        if any(word in top_words for word in ["personnel", "chef", "commerciaux", "sympathique"]):
            meanings.append("Expérience avec le personnel")
        if any(word in top_words for word in ["encore", "pire", "nulle", "ouverture"]):
            meanings.append("Problèmes et insatisfactions")

        # Si aucune signification spécifique n'est trouvée, ajouter "Autre sujet bancaire"
        if not meanings:
            meanings.append("Autre sujet bancaire")

        topic_descriptions[topic_id] = ", ".join(meanings)  # Stocker les significations sous forme de chaîne

    return topic_descriptions

try:

    conn = connect_to_aiven_db()
    if not conn:
        raise Exception("Failed to connect to the database.")
    cursor = conn.cursor()

    # Récupération des données depuis la table all_bank_reviews
    query = """
        SELECT id, clean_review, language
        FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Conversion en DataFrame Pandas
    columns = ["id", "clean_review", "language"]
    df = pd.DataFrame(rows, columns=columns)

    # Gestion des langues manquantes ou inconnues
    df['language'] = df['language'].fillna("fr")  # Remplacer les valeurs NULL par "fr"
    df['language'] = df.apply(lambda row: detect_language(row['clean_review']) if row['language'] not in supported_languages else row['language'], axis=1)

    # Prétraitement des avis en fonction de la langue détectée
    df['processed_review'] = df.apply(lambda row: preprocess(row['clean_review'], row['language']), axis=1)

    # Création du dictionnaire et du corpus pour LDA
    dictionary = Dictionary(df['processed_review'])
    dictionary.filter_extremes(no_below=2, no_above=0.5)
    corpus = [dictionary.doc2bow(doc) for doc in df['processed_review']]

    # Entraînement du modèle LDA
    num_topics = 10  # Nombre de sujets à extraire
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

    # Extraire les mots-clés pour chaque topic
    topic_keywords = extract_topic_keywords(lda_model, dictionary, num_topics)

    # Attribuer plusieurs significations spécifiques à chaque topic
    topic_meanings = extract_topic_meanings(topic_keywords)

    # Afficher la correspondance explicite entre les topics et leurs significations
    print("=== Correspondance entre les Topics et leurs Significations ===")
    for topic_id, meaning in topic_meanings.items():
        print(f"Topic {topic_id}: {meaning}")

    # Extraction des sujets pour chaque avis
    def extract_topic(review_bow):
        topic_probs = lda_model.get_document_topics(review_bow, minimum_probability=0.01)
        top_topic = max(topic_probs, key=lambda x: x[1])[0]  # Sujet dominant
        return top_topic

    df['topic'] = [extract_topic(dictionary.doc2bow(doc)) for doc in df['processed_review']]

    # Ajouter les significations spécifiques pour chaque avis
    df['topic_meaning'] = df['topic'].map(topic_meanings)

    # Vérifier si les colonnes 'topic' et 'topic_meaning' existent déjà dans la table
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'clean_reviews' AND column_name IN ('topic', 'topic_meaning');
    """)
    existing_columns = [row[0] for row in cursor.fetchall()]

    # Ajouter les colonnes manquantes
    if 'topic' not in existing_columns:
        cursor.execute("ALTER TABLE transactional.clean_reviews ADD COLUMN topic INTEGER;")
    if 'topic_meaning' not in existing_columns:
        cursor.execute("ALTER TABLE transactional.clean_reviews ADD COLUMN topic_meaning TEXT;")

    # Mise à jour des colonnes 'topic' et 'topic_meaning' pour chaque avis
    update_query = """
        UPDATE transactional.clean_reviews
        SET topic = %s, topic_meaning = %s
        WHERE id = %s;
    """

    for _, row in df.iterrows():
        cursor.execute(update_query, (
            row['topic'],
            row['topic_meaning'],
            row['id']
        ))

    conn.commit()
    print("✅ Colonnes 'topic' et 'topic_meaning' mises à jour avec succès.")

except Exception as e:
    print(f"❌ Erreur PostgreSQL : {e}")
    logging.error(f"Erreur critique : {e}")

finally:
    # Fermer le curseur et la connexion
    if cursor:
        cursor.close()
    if conn:
        conn.close()