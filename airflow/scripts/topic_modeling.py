# import psycopg2
# import spacy
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.decomposition import LatentDirichletAllocation

# # Charger le modèle SpaCy pour le prétraitement NLP
# nlp = spacy.load("en_core_web_sm")

# # Connexion à PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# # Ajouter la colonne topics si elle n'existe pas
# cur.execute("""
#     ALTER TABLE transactional.clean_reviews 
#     ADD COLUMN IF NOT EXISTS topics TEXT;
# """)
# conn.commit()

# # Récupérer les avis nettoyés
# cur.execute("SELECT id, clean_review FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
# rows = cur.fetchall()

# # Prétraitement du texte avec SpaCy
# texts = []
# ids = []
# for row in rows:
#     review_id = row[0]
#     text = row[1]

#     doc = nlp(text.lower())
#     tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]

#     texts.append(" ".join(tokens))
#     ids.append(review_id)

# # Vectorisation avec CountVectorizer
# vectorizer = CountVectorizer(max_features=1000, stop_words='english')
# X = vectorizer.fit_transform(texts)

# # Modèle LDA pour extraire les sujets
# lda = LatentDirichletAllocation(n_components=5, random_state=42)
# topics = lda.fit_transform(X)

# # Assigner le sujet dominant à chaque avis
# for i, topic_distribution in enumerate(topics):
#     topic_id = topic_distribution.argmax()
#     topic_words = [vectorizer.get_feature_names_out()[j] for j in lda.components_[topic_id].argsort()[-5:]]
#     topic_label = ", ".join(topic_words)

#     # Mise à jour dans clean_reviews
#     cur.execute("UPDATE transactional.clean_reviews SET topics = %s WHERE id = %s;", (topic_words, ids[i]))


# conn.commit()
# cur.close()
# conn.close()

# print("✅ Modèle LDA appliqué avec succès.")



# import psycopg2
# import spacy
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import LatentDirichletAllocation

# # Charger les modèles SpaCy pour différentes langues
# nlp_models = {
#     "en": spacy.load("en_core_web_sm"),
#     "fr": spacy.load("fr_core_news_sm"),
#     "es": spacy.load("es_core_news_sm"),
#     "de": spacy.load("de_core_news_sm"),
#     "ar": spacy.load("ar_core_news_sm"),  # Ajout du support pour l'arabe
# }

# try:
#     from farasa.segmenter import FarasaSegmenter
#     farasa_segmenter = FarasaSegmenter(interactive=True)  # Améliore le prétraitement arabe
# except:
#     farasa_segmenter = None
#     print("⚠️ Farasa non installé. L'arabe sera traité uniquement avec SpaCy.")

# # Connexion PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# # Récupérer les avis nettoyés avec leur langue
# cur.execute("SELECT id, clean_review, language FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
# rows = cur.fetchall()

# # Prétraitement des textes
# texts = []
# ids = []
# for row in rows:
#     review_id = row[0]
#     text = row[1]
#     lang = row[2]  # On récupère la langue déjà stockée

#     if lang in nlp_models:
#         nlp = nlp_models[lang]

#         if lang == "ar" and farasa_segmenter:
#             text = " ".join(farasa_segmenter.segment(text))  # Segmentation arabe

#         doc = nlp(text.lower())
#         tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
#         processed_text = " ".join(tokens)
#     else:
#         processed_text = text  # Si la langue n'est pas supportée, garder le texte brut

#     texts.append(processed_text)
#     ids.append(review_id)

# # Vectorisation avec TfidfVectorizer
# vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
# X = vectorizer.fit_transform(texts)

# # Modèle LDA pour extraire les sujets
# lda = LatentDirichletAllocation(n_components=5, random_state=42, n_jobs=-1)
# topics = lda.fit_transform(X)

# # Assigner le sujet dominant à chaque avis
# for i, topic_distribution in enumerate(topics):
#     topic_id = topic_distribution.argmax()
#     topic_words = [vectorizer.get_feature_names_out()[j] for j in lda.components_[topic_id].argsort()[-5:]]
#     topic_label = ", ".join(topic_words)

#     # Mise à jour de la table enrichie avec les topics
#     cur.execute("""
#         UPDATE transactional.clean_reviews 
#         SET topics = %s 
#         WHERE id = %s;
#     """, (topic_label, ids[i]))

# # Valider et fermer la connexion
# conn.commit()
# cur.close()
# conn.close()

# print("✅ Extraction des sujets terminée avec succès ! 🚀")

# import psycopg2
# import spacy
# from googletrans import Translator
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import LatentDirichletAllocation

# # Charger les modèles SpaCy pour différentes langues
# nlp_models = {
#     "en": spacy.load("en_core_web_sm"),
#     "fr": spacy.load("fr_core_news_sm"),
#     "es": spacy.load("es_core_news_sm"),
#     "de": spacy.load("de_core_news_sm"),
#     "ar": spacy.load("ar_core_news_sm"),  # Ajout du support pour l'arabe
# }

# # Connexion PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()


# # Ensure the sentiment column exists
# cur.execute("""
#     ALTER TABLE transactional.clean_reviews 
#     ADD COLUMN IF NOT EXISTS sentiment TEXT;
# """)
# conn.commit()


# # Initialiser le traducteur Google
# translator = Translator()

# # Récupérer les avis nettoyés avec leur langue
# cur.execute("SELECT id, clean_review, language FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
# rows = cur.fetchall()

# # Prétraitement des textes
# texts = []
# ids = []
# for row in rows:
#     review_id = row[0]
#     text = row[1]
#     lang = row[2]  # On récupère la langue déjà stockée

#     if lang == "ar":
#         # Traduire le texte arabe en anglais avant le traitement
#         translated = translator.translate(text, src='ar', dest='en')
#         text = translated.text  # Texte traduit en anglais

#     if lang in nlp_models:
#         nlp = nlp_models[lang]

#         doc = nlp(text.lower())
#         tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
#         processed_text = " ".join(tokens)
#     else:
#         processed_text = text  # Si la langue n'est pas supportée, garder le texte brut

#     texts.append(processed_text)
#     ids.append(review_id)

# # Vectorisation avec TfidfVectorizer
# vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
# X = vectorizer.fit_transform(texts)

# # Modèle LDA pour extraire les sujets
# lda = LatentDirichletAllocation(n_components=5, random_state=42, n_jobs=-1)
# topics = lda.fit_transform(X)

# # Assigner le sujet dominant à chaque avis
# for i, topic_distribution in enumerate(topics):
#     topic_id = topic_distribution.argmax()
#     topic_words = [vectorizer.get_feature_names_out()[j] for j in lda.components_[topic_id].argsort()[-5:]]
#     topic_label = ", ".join(topic_words)

#     # Si le texte était arabe, traduire le résultat des topics en arabe
#     if rows[i][2] == "ar":
#         topic_label_F = translator.translate(topic_label, src='en', dest='ar').text
#     else:
#         topic_label_F = topic_label  # Pas de traduction nécessaire pour les autres langues

#     # Mise à jour de la table enrichie avec les topics
#     cur.execute("""
#         UPDATE transactional.clean_reviews 
#         SET topics = %s
#         WHERE id = %s;
#     """, (topic_label_F, ids[i]))

# # Valider et fermer la connexion
# conn.commit()
# cur.close()
# conn.close()

# print("✅ Extraction des sujets terminée avec succès ! 🚀")



# import psycopg2
# import spacy
# from googletrans import Translator
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import LatentDirichletAllocation

# # Charger les modèles SpaCy pour différentes langues (sans le modèle arabe)
# nlp_models = {
#     "en": spacy.load("en_core_web_sm"),
#     "fr": spacy.load("fr_core_news_sm"),
#     "es": spacy.load("es_core_news_sm"),
#     "de": spacy.load("de_core_news_sm"),
# }

# # Connexion PostgreSQL
# conn = psycopg2.connect(
#     dbname="project_data_wherhouse",
#     user="user_project",
#     password="2002",
#     host="localhost",
#     port="5432"
# )
# cur = conn.cursor()

# # S'assurer que la colonne 'topics' existe
# cur.execute("""
#     ALTER TABLE transactional.clean_reviews 
#     ADD COLUMN IF NOT EXISTS topics TEXT;
# """)
# conn.commit()

# # Initialiser le traducteur Google
# translator = Translator()

# # Récupérer les avis nettoyés avec leur langue
# cur.execute("SELECT id, clean_review, language FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
# rows = cur.fetchall()

# # Prétraitement des textes
# texts = []
# ids = []
# for row in rows:
#     review_id = row[0]
#     text = row[1]
#     lang = row[2]  # On récupère la langue déjà stockée

#     try:
#         if lang == "ar":
#             # Traduire le texte arabe en anglais avant le traitement
#             translated = translator.translate(text, src='ar', dest='en')
#             text = translated.text  # Texte traduit en anglais
#             lang = "en"  # Traiter le texte comme étant en anglais

#         if lang in nlp_models:
#             nlp = nlp_models[lang]

#             doc = nlp(text.lower())
#             tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
#             processed_text = " ".join(tokens)
#         else:
#             processed_text = text  # Si la langue n'est pas supportée, garder le texte brut

#         texts.append(processed_text)
#         ids.append(review_id)

#     except Exception as e:
#         print(f"Erreur lors du traitement de la critique {review_id} : {e}")

# # Vectorisation avec TfidfVectorizer
# vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
# X = vectorizer.fit_transform(texts)

# # Modèle LDA pour extraire les sujets
# lda = LatentDirichletAllocation(n_components=5, random_state=42, n_jobs=-1)
# topics = lda.fit_transform(X)

# # Assigner le sujet dominant à chaque avis
# for i, topic_distribution in enumerate(topics):
#     topic_id = topic_distribution.argmax()
#     topic_words = [vectorizer.get_feature_names_out()[j] for j in lda.components_[topic_id].argsort()[-5:]]
#     topic_label = " ".join(topic_words)

#     # Si le texte était arabe, traduire le résultat des topics en arabe
#     if rows[i][2] == "ar":
#         topic_label = translator.translate(topic_label, src='en', dest='ar').text

#     # Mise à jour de la table enrichie avec les topics
#     cur.execute("""
#         UPDATE transactional.clean_reviews 
#         SET topics = %s
#         WHERE id = %s;
#     """, (topic_label, ids[i]))

# # Valider et fermer la connexion
# conn.commit()
# cur.close()
# conn.close()

# print("✅ Extraction des sujets terminée avec succès ! 🚀")


# import psycopg2
# import spacy
# from googletrans import Translator
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import LatentDirichletAllocation
# import logging

# # Configuration de la journalisation pour suivre les erreurs
# logging.basicConfig(filename='lda_errors.log', level=logging.ERROR)

# # Charger les modèles SpaCy pour différentes langues (sans le modèle arabe)
# nlp_models = {
#     "en": spacy.load("en_core_web_sm"),
#     "fr": spacy.load("fr_core_news_sm"),
#     "es": spacy.load("es_core_news_sm"),
#     "de": spacy.load("de_core_news_sm"),
# }

# # Connexion PostgreSQL
# try:
#     conn = psycopg2.connect(
#         dbname="project_data_wherhouse",
#         user="user_project",
#         password="2002",
#         host="localhost",
#         port="5432"
#     )
#     cur = conn.cursor()
# except Exception as e:
#     logging.error(f"Erreur lors de la connexion à la base de données : {e}")
#     raise

# # S'assurer que la colonne 'topics' existe
# try:
#     cur.execute("""
#         ALTER TABLE transactional.clean_reviews 
#         ADD COLUMN IF NOT EXISTS topics TEXT;
#     """)
#     conn.commit()
# except Exception as e:
#     logging.error(f"Erreur lors de la création de la colonne 'topics' : {e}")
#     raise

# # Initialiser le traducteur Google
# translator = Translator()

# # Récupérer les avis nettoyés avec leur langue
# try:
#     cur.execute("SELECT id, clean_review, language FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
#     rows = cur.fetchall()
# except Exception as e:
#     logging.error(f"Erreur lors de la récupération des données : {e}")
#     raise

# # Prétraitement des textes
# texts = []
# ids = []
# for row in rows:
#     review_id = row[0]
#     text = row[1]
#     lang = row[2]  # On récupère la langue déjà stockée

#     try:
#         if lang == "ar":
#             # Traduire le texte arabe en anglais avant le traitement
#             translated = translator.translate(text, src='ar', dest='en')
#             text = translated.text  # Texte traduit en anglais
#             lang = "en"  # Traiter le texte comme étant en anglais

#         if lang in nlp_models:
#             nlp = nlp_models[lang]

#             doc = nlp(text.lower())
#             tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
#             processed_text = " ".join(tokens)
#         else:
#             processed_text = text  # Si la langue n'est pas supportée, garder le texte brut

#         texts.append(processed_text)
#         ids.append(review_id)

#     except Exception as e:
#         logging.error(f"Erreur lors du prétraitement de la critique {review_id} : {e}")

# # Vectorisation avec TfidfVectorizer
# vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
# X = vectorizer.fit_transform(texts)

# # Modèle LDA pour extraire les sujets
# lda = LatentDirichletAllocation(n_components=5, random_state=42, n_jobs=-1)
# lda.fit(X)

# # Afficher les sujets extraits
# def display_topics(model, feature_names, num_top_words):
#     for idx, topic in enumerate(model.components_):
#         print(f"Sujet {idx + 1}: {' '.join([feature_names[i] for i in topic.argsort()[:-num_top_words - 1:-1]])}")

# print("=== Sujets Extraits ===")
# display_topics(lda, vectorizer.get_feature_names_out(), 5)

# # Assigner le sujet dominant à chaque avis
# topics_results = lda.transform(X)
# for i, topic_distribution in enumerate(topics_results):
#     topic_id = topic_distribution.argmax()
#     topic_words = [vectorizer.get_feature_names_out()[j] for j in lda.components_[topic_id].argsort()[-5:]]
#     topic_label = " ".join(topic_words)

#     # Si le texte était arabe, traduire le résultat des topics en arabe
#     if rows[i][2] == "ar":
#         try:
#             topic_label = translator.translate(topic_label, src='en', dest='ar').text
#         except Exception as e:
#             logging.error(f"Erreur lors de la traduction du sujet pour l'avis {ids[i]} : {e}")

#     # Mise à jour de la table enrichie avec les topics
#     try:
#         cur.execute("""
#             UPDATE transactional.clean_reviews 
#             SET topics = %s
#             WHERE id = %s;
#         """, (topic_label, ids[i]))
#     except Exception as e:
#         logging.error(f"Erreur lors de la mise à jour de la base de données pour l'avis {ids[i]} : {e}")

# # Valider et fermer la connexion
# try:
#     conn.commit()
#     cur.close()
#     conn.close()
# except Exception as e:
#     logging.error(f"Erreur lors de la validation ou de la fermeture de la connexion : {e}")

# print("✅ Extraction des sujets terminée avec succès ! 🚀")

# import psycopg2
# import spacy
# from googletrans import Translator
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.decomposition import LatentDirichletAllocation
# import logging

# # Configuration de la journalisation pour suivre les erreurs
# logging.basicConfig(filename='lda_errors.log', level=logging.ERROR)

# # Charger les modèles SpaCy pour différentes langues (sans le modèle arabe)
# nlp_models = {
#     "en": spacy.load("en_core_web_sm"),
#     "fr": spacy.load("fr_core_news_sm"),
#     "es": spacy.load("es_core_news_sm"),
#     "de": spacy.load("de_core_news_sm"),
# }

# # Connexion PostgreSQL
# try:
#     conn = psycopg2.connect(
#         dbname="project_data_wherhouse",
#         user="user_project",
#         password="2002",
#         host="localhost",
#         port="5432"
#     )
#     cur = conn.cursor()
# except Exception as e:
#     logging.error(f"Erreur lors de la connexion à la base de données : {e}")
#     raise

# # S'assurer que la colonne 'topics' existe
# try:
#     cur.execute("""
#         ALTER TABLE transactional.clean_reviews 
#         ADD COLUMN IF NOT EXISTS topics TEXT;
#     """)
#     conn.commit()
# except Exception as e:
#     logging.error(f"Erreur lors de la création de la colonne 'topics' : {e}")
#     raise

# # Initialiser le traducteur Google
# translator = Translator()

# # Récupérer les avis nettoyés avec leur langue
# try:
#     cur.execute("SELECT id, clean_review, language FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
#     rows = cur.fetchall()
# except Exception as e:
#     logging.error(f"Erreur lors de la récupération des données : {e}")
#     raise

# # Prétraitement des textes
# texts = []
# ids = []
# for row in rows:
#     review_id = row[0]
#     text = row[1]
#     lang = row[2]  # On récupère la langue déjà stockée

#     try:
#         if lang == "ar":
#             # Traduire le texte arabe en anglais avant le traitement
#             translated = translator.translate(text, src='ar', dest='en')
#             text = translated.text  # Texte traduit en anglais
#             lang = "en"  # Traiter le texte comme étant en anglais

#         if lang in nlp_models:
#             nlp = nlp_models[lang]

#             doc = nlp(text.lower())
#             tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
#             processed_text = " ".join(tokens)
#         else:
#             processed_text = text  # Si la langue n'est pas supportée, garder le texte brut

#         texts.append(processed_text)
#         ids.append(review_id)

#     except Exception as e:
#         logging.error(f"Erreur lors du prétraitement de la critique {review_id} : {e}")

# # Vectorisation avec TfidfVectorizer
# vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
# X = vectorizer.fit_transform(texts)

# # Modèle LDA pour extraire les sujets
# lda = LatentDirichletAllocation(n_components=5, random_state=42, n_jobs=-1)
# lda.fit(X)

# # Afficher les sujets extraits
# def display_topics(model, feature_names, num_top_words):
#     for idx, topic in enumerate(model.components_):
#         print(f"Sujet {idx + 1}: {' '.join([feature_names[i] for i in topic.argsort()[:-num_top_words - 1:-1]])}")

# print("=== Sujets Extraits ===")
# display_topics(lda, vectorizer.get_feature_names_out(), 5)

# # Assigner le sujet dominant à chaque avis
# topics_results = lda.transform(X)
# for i, topic_distribution in enumerate(topics_results):
#     topic_id = topic_distribution.argmax()
#     topic_words = [vectorizer.get_feature_names_out()[j] for j in lda.components_[topic_id].argsort()[-5:]]
#     topic_label = " ".join(topic_words)

#     # Si le texte était arabe, traduire le résultat des topics en arabe
#     if rows[i][2] == "ar":
#         try:
#             topic_label = translator.translate(topic_label, src='en', dest='ar').text
#         except Exception as e:
#             logging.error(f"Erreur lors de la traduction du sujet pour l'avis {ids[i]} : {e}")

#     # Mise à jour de la table enrichie avec les topics
#     try:
#         cur.execute("""
#             UPDATE transactional.clean_reviews 
#             SET topics = %s
#             WHERE id = %s;
#         """, (topic_label, ids[i]))
#     except Exception as e:
#         logging.error(f"Erreur lors de la mise à jour de la base de données pour l'avis {ids[i]} : {e}")

# # Valider et fermer la connexion
# try:
#     conn.commit()
#     cur.close()
#     conn.close()
# except Exception as e:
#     logging.error(f"Erreur lors de la validation ou de la fermeture de la connexion : {e}")

# print("✅ Extraction des sujets terminée avec succès ! 🚀")

# import psycopg2
# from psycopg2 import sql
# from langdetect import detect
# from sklearn.feature_extraction.text import TfidfVectorizer
# from gensim.models.ldamodel import LdaModel
# from gensim.corpora.dictionary import Dictionary
# from transformers import pipeline
# import spacy
# import logging
# import time

# # Configuration de la journalisation
# logging.basicConfig(
#     filename='lda_pipeline.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# # Charger SpaCy modèle multilingue
# nlp = spacy.load("xx_ent_wiki_sm")

# # Initialiser le traducteur Hugging Face
# translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ar-en")

# # Connexion à la base de données
# def connect_to_db():
#     try:
#         conn = psycopg2.connect(
#             dbname="project_data_wherhouse",
#             user="user_project",
#             password="2002",
#             host="localhost",
#             port="5432"
#         )
#         cur = conn.cursor()
#         logging.info("Connexion à la base de données réussie.")
#         return conn, cur
#     except Exception as e:
#         logging.error(f"Erreur lors de la connexion à la base de données : {e}")
#         raise

# # Prétraitement des textes
# def preprocess_text(text, lang="en"):
#     try:
#         if lang == "ar":
#             # Traduire en anglais
#             translated = translator(text)[0]['translation_text']
#             text = translated
#             lang = "en"

#         doc = nlp(text.lower())
#         tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
#         return " ".join(tokens)
#     except Exception as e:
#         logging.error(f"Erreur lors du prétraitement : {e}")
#         return ""

# # Vectorisation avec TF-IDF
# def vectorize_texts(texts):
#     vectorizer = TfidfVectorizer(max_features=1000)
#     X = vectorizer.fit_transform(texts)
#     return X, vectorizer

# # Modèle LDA avec Gensim
# def train_lda_model(corpus, id2word):
#     lda_model = LdaModel(
#         corpus=corpus,
#         id2word=id2word,
#         num_topics=10,
#         random_state=42,
#         passes=10
#     )
#     return lda_model

# # Mapping des topics aux catégories métier
# topics_mapping = {
#     "service client expérience satisfaction assistance": "Service Client",
#     "compte carte prêt épargne banque": "Produits Bancaires",
#     "frais commission coût gratuit": "Frais et Tarifs",
#     "application interface mobile connexion": "Expérience Numérique",
#     "sécurité confidentialité données protection": "Sécurité et Confidentialité",
# }

# def map_topic_to_category(topic_words):
#     min_match_threshold = 3
#     max_match_count = 0
#     best_category = "Inconnu"
#     topic_words_set = set(topic_words.split())

#     for keywords, category in topics_mapping.items():
#         mapping_words = set(keywords.split())
#         match_count = len(topic_words_set.intersection(mapping_words))

#         if match_count >= min_match_threshold and match_count > max_match_count:
#             max_match_count = match_count
#             best_category = category

#     return best_category

# # Mise à jour de la base de données
# def update_database(conn, cur, ids, topics, categories):
#     batch_size = 100
#     try:
#         for i in range(0, len(ids), batch_size):
#             batch_ids = ids[i:i + batch_size]
#             batch_topics = topics[i:i + batch_size]
#             batch_categories = categories[i:i + batch_size]

#             query = sql.SQL("""
#                 UPDATE transactional.clean_reviews
#                 SET topics = %s, topic_category = %s
#                 WHERE id = %s;
#             """)
#             cur.executemany(query, zip(batch_topics, batch_categories, batch_ids))
#             conn.commit()
#         logging.info("Mise à jour de la base de données terminée.")
#     except Exception as e:
#         logging.error(f"Erreur lors de la mise à jour de la base de données : {e}")

# # Pipeline principal

# start_time = time.time()
# conn, cur = connect_to_db()

# # Récupérer les critiques
# cur.execute("SELECT id, clean_review, language FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;")
# rows = cur.fetchall()

# # Prétraitement
# texts, ids = [], []
# for row in rows:
#     review_id, text, lang = row
#     processed_text = preprocess_text(text, lang)
#     if processed_text:
#         texts.append(processed_text)
#         ids.append(review_id)

# # Vectorisation
# X, vectorizer = vectorize_texts(texts)

# # Création du dictionnaire et du corpus pour Gensim
# dictionary = Dictionary([text.split() for text in texts])
# corpus = [dictionary.doc2bow(text.split()) for text in texts]

# # Entraîner le modèle LDA
# lda_model = train_lda_model(corpus, dictionary)

# # Extraire les sujets dominants
# topics, categories = [], []
# for i, bow in enumerate(corpus):
#     topic_distribution = lda_model.get_document_topics(bow)
#     dominant_topic = max(topic_distribution, key=lambda x: x[1])[0]
#     topic_words = " ".join([word for word, _ in lda_model.show_topic(dominant_topic)])
#     topic_category = map_topic_to_category(topic_words)
#     topics.append(topic_words)
#     categories.append(topic_category)

# # Mise à jour de la base de données
# update_database(conn, cur, ids, topics, categories)

# # Fermer la connexion
# cur.close()
# conn.close()

# end_time = time.time()
# logging.info(f"Pipeline terminé en {end_time - start_time:.2f} secondes.")


# import os
# import psycopg2
# import pandas as pd
# import nltk
# from nltk.corpus import stopwords
# from gensim.corpora import Dictionary
# from gensim.models import LdaModel
# import spacy

# # Télécharger les ressources NLTK nécessaires
# nltk.download('stopwords')

# # Charger SpaCy pour différentes langues
# spacy_languages = {
#     "en": spacy.load("en_core_web_sm"),
#     "fr": spacy.load("fr_core_news_sm"),
#     "es": spacy.load("es_core_news_sm"),
#     "de": spacy.load("de_core_news_sm")
# }

# # Liste des langues prises en charge
# supported_languages = list(spacy_languages.keys())

# # Configuration de la connexion PostgreSQL
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_NAME = os.getenv("DB_NAME", "project_data_wherhouse")
# DB_USER = os.getenv("DB_USER", "user_project")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "2002")

# # Prétraitement du texte en fonction de la langue
# def preprocess(text, language="fr"):
#     if language == "ar":
#         # Prétraitement spécifique pour l'arabe (ex. avec camel-tools)
#         raise NotImplementedError("Prétraitement pour l'arabe non implémenté.")
#     if language == "unknown":
#         print(f"⚠️ Langue inconnue détectée pour le texte : {text[:50]}...")
#         language = "fr"  # Utiliser une langue par défaut
#     nlp = spacy_languages.get(language)
#     if not nlp:
#         raise ValueError(f"Langue {language} non prise en charge.")
    
#     doc = nlp(text.lower())  # Tokenisation et mise en minuscules
#     tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]  # Lemmatisation et suppression des stopwords
#     return tokens

# # Extraction des mots-clés pour chaque topic
# def extract_topic_keywords(lda_model, dictionary, num_topics):
#     topic_keywords = {}
#     for topic_id in range(num_topics):
#         words = lda_model.show_topic(topic_id, topn=10)  # Récupérer les 10 mots-clés principaux
#         keywords = [word for word, _ in words]
#         topic_keywords[topic_id] = keywords
#     return topic_keywords

# # Fonction pour extraire plusieurs significations pour chaque topic
# def extract_topic_meanings(topic_words):
#     topic_descriptions = {}

#     for topic_id, top_words in topic_words.items():
#         meanings = []

#         if any(word in top_words for word in ["service", "bon", "avis", "accompagner"]):
#             meanings.append("Qualité du service et relation client")
#         if any(word in top_words for word in ["frais", "carte", "guichet", "plus"]):
#             meanings.append("Frais bancaires et gestion des comptes")
#         if any(word in top_words for word in ["dattente", "minutes", "agent", "sécurité"]):
#             meanings.append("Temps d'attente et gestion en agence")
#         if any(word in top_words for word in ["personnel", "chef", "commerciaux", "sympathique"]):
#             meanings.append("Expérience avec le personnel")
#         if any(word in top_words for word in ["encore", "pire", "nulle", "ouverture"]):
#             meanings.append("Problèmes et insatisfactions")

#         # Si aucune signification spécifique n'est trouvée, ajouter "Autre sujet bancaire"
#         if not meanings:
#             meanings.append("Autre sujet bancaire")

#         topic_descriptions[topic_id] = ", ".join(meanings)  # Stocker les significations sous forme de chaîne

#     return topic_descriptions

# try:
#     # Connexion à la base de données
#     conn = psycopg2.connect(
#         host=DB_HOST,
#         database=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD
#     )
#     cursor = conn.cursor()

#     # Récupération des données depuis la table all_bank_reviews
#     query = """
#         SELECT id, clean_review, language
#         FROM transactional.clean_reviews WHERE clean_review IS NOT NULL;
#     """
#     cursor.execute(query)
#     rows = cursor.fetchall()

#     # Conversion en DataFrame Pandas
#     columns = ["id", "clean_review", "language"]
#     df = pd.DataFrame(rows, columns=columns)

#     # Prétraitement des avis en fonction de la langue détectée
#     df['processed_review'] = df.apply(lambda row: preprocess(row['clean_review'], row['language']), axis=1)

#     # Création du dictionnaire et du corpus pour LDA
#     dictionary = Dictionary(df['processed_review'])
#     dictionary.filter_extremes(no_below=2, no_above=0.5)
#     corpus = [dictionary.doc2bow(doc) for doc in df['processed_review']]

#     # Entraînement du modèle LDA
#     num_topics = 10  # Nombre de sujets à extraire
#     lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

#     # Extraire les mots-clés pour chaque topic
#     topic_keywords = extract_topic_keywords(lda_model, dictionary, num_topics)

#     # Attribuer plusieurs significations spécifiques à chaque topic
#     topic_meanings = extract_topic_meanings(topic_keywords)

#     # Afficher la correspondance explicite entre les topics et leurs significations
#     print("=== Correspondance entre les Topics et leurs Significations ===")
#     for topic_id, meaning in topic_meanings.items():
#         print(f"Topic {topic_id}: {meaning}")

#     # Extraction des sujets pour chaque avis
#     def extract_topic(review_bow):
#         topic_probs = lda_model.get_document_topics(review_bow, minimum_probability=0.01)
#         top_topic = max(topic_probs, key=lambda x: x[1])[0]  # Sujet dominant
#         return top_topic

#     df['topic'] = [extract_topic(dictionary.doc2bow(doc)) for doc in df['processed_review']]

#     # Ajouter les significations spécifiques pour chaque avis
#     df['topic_meaning'] = df['topic'].map(topic_meanings)

#     # Vérifier si les colonnes 'topic' et 'topic_meaning' existent déjà dans la table
#     cursor.execute("""
#         SELECT column_name
#         FROM information_schema.columns
#         WHERE table_name = 'clean_reviews' AND column_name IN ('topic', 'topic_meaning');
#     """)
#     existing_columns = [row[0] for row in cursor.fetchall()]

#     # Ajouter les colonnes manquantes
#     if 'topic' not in existing_columns:
#         cursor.execute("ALTER TABLE transactional.clean_reviews ADD COLUMN topic INTEGER;")
#     if 'topic_meaning' not in existing_columns:
#         cursor.execute("ALTER TABLE transactional.clean_reviews ADD COLUMN topic_meaning TEXT;")

#     # Mettre à jour les colonnes 'topic' et 'topic_meaning' pour chaque avis
#     update_query = """
#         UPDATE transactional.clean_reviews
#         SET topic = %s, topic_meaning = %s
#         WHERE id = %s;
#     """

#     for _, row in df.iterrows():
#         cursor.execute(update_query, (
#             row['topic'],
#             row['topic_meaning'],
#             row['id']
#         ))

#     conn.commit()
#     print("✅ Colonnes 'topic' et 'topic_meaning' mises à jour avec succès.")

# except Exception as e:
#     print(f"❌ Erreur PostgreSQL : {e}")

# finally:
#     # Fermer le curseur et la connexion
#     if cursor:
#         cursor.close()
#     if conn:
#         conn.close()

import os
import psycopg2
import pandas as pd
import nltk
from nltk.corpus import stopwords
from gensim.corpora import Dictionary
from gensim.models import LdaModel
import spacy
from langdetect import detect
import logging
from connect_to_db import connect_to_aiven_db

# Configuration des logs
logging.basicConfig(filename='errors.log', level=logging.WARNING)

# Télécharger les ressources NLTK nécessaires
nltk.download('stopwords')

# Charger SpaCy pour différentes langues
spacy_languages = {
    "en": spacy.load("en_core_web_sm"),
    "fr": spacy.load("fr_core_news_sm"),
    "es": spacy.load("es_core_news_sm"),
    "de": spacy.load("de_core_news_sm")
}

# Liste des langues prises en charge
supported_languages = list(spacy_languages.keys())

# Configuration de la connexion PostgreSQL
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_NAME = os.getenv("DB_NAME", "project_data_wherhouse")
# DB_USER = os.getenv("DB_USER", "user_project")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "2002")

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
    # Connexion à la base de données
    # conn = psycopg2.connect(
    #     host=DB_HOST,
    #     database=DB_NAME,
    #     user=DB_USER,
    #     password=DB_PASSWORD
    # )
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