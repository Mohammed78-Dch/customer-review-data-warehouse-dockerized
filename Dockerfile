# FROM python:3.11.11

# # Variables Airflow
# ENV AIRFLOW_VERSION=2.8.1
# ENV CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.11.txt"
# ENV AIRFLOW_HOME=/opt/airflow
# ENV AIRFLOW_UID=50000
# ENV AIRFLOW_GID=50000

# # Installer dépendances système
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     bash build-essential libpq-dev netcat-openbsd git wget curl gnupg unzip ca-certificates python3-pip \
#     fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 \
#     libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 \
#     libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxkbcommon0 \
#     libwayland-client0 xdg-utils libu2f-udev libvulkan1 \
#     && rm -rf /var/lib/apt/lists/*

# # Installer Google Chrome (stable) avec bonne clé GPG
# RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg \
#     && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable \
#     && rm -rf /var/lib/apt/lists/*



# # Installer ChromeDriver compatible (via canal officiel Chrome for Testing)
# RUN set -eux; \
#     CHROMEDRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json \
#         | python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])"); \
#     echo "⬇️  Downloading ChromeDriver version: $CHROMEDRIVER_VERSION"; \
#     curl -sSL "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -o /tmp/chromedriver.zip; \
#     unzip /tmp/chromedriver.zip -d /usr/local/bin/; \
#     mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
#     chmod +x /usr/local/bin/chromedriver; \
#     rm -rf /tmp/chromedriver.zip /usr/local/bin/chromedriver-linux64

# # Créer utilisateur airflow
# RUN groupadd -g ${AIRFLOW_GID} airflow \
#     && useradd -m -u ${AIRFLOW_UID} -g airflow -s /bin/bash airflow

# # Installer Airflow avec les contraintes officielles
# RUN pip install --upgrade pip setuptools wheel \
#     && pip install "apache-airflow[celery,postgres,redis]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir --retries 5 --timeout 60 -r /tmp/requirements.txt && rm /tmp/requirements.txt

# # Installer manuellement les modèles SpaCy (si pas dans requirements)
# RUN python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
#  && python -m pip install https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl \
#  && python -m pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.8.0/es_core_news_sm-3.8.0-py3-none-any.whl  \
#  && python -m pip install https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-3.8.0/de_core_news_sm-3.8.0-py3-none-any.whl

# # Créer les répertoires Airflow
# RUN mkdir -p ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/plugins ${AIRFLOW_HOME}/config \
#     && chown -R airflow:airflow ${AIRFLOW_HOME}

# # Copier le script d’entrée
# COPY entrypoint.sh /entrypoint
# RUN chmod +x /entrypoint

# # Passer en utilisateur airflow
# USER airflow
# WORKDIR ${AIRFLOW_HOME}
# ENV PATH="${AIRFLOW_HOME}/.local/bin:$PATH"

# # Exposer port webserver Airflow
# EXPOSE 8080

# # Healthcheck (optionnel)
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8080/health || exit 1

# # Entrypoint et commande par défaut
# ENTRYPOINT ["/entrypoint"]
# CMD ["airflow", "scheduler"]


# FROM python:3.11-slim

# # Variables d'environnement
# ENV AIRFLOW_VERSION=2.10.5
# ENV CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt"
# ENV AIRFLOW_HOME=/opt/airflow
# ENV AIRFLOW_UID=50000
# ENV AIRFLOW_GID=50000
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PIP_NO_CACHE_DIR=1
# ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# # Installation des dépendances système
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     # Dépendances de base
#     bash build-essential curl wget gnupg unzip ca-certificates \
#     libpq-dev netcat-openbsd git procps \
#     # Dépendances pour Chrome/Selenium
#     fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
#     libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 \
#     libgtk-3-0 libnspr4 libnss3 libxcomposite1 libxdamage1 \
#     libxfixes3 libxrandr2 libxkbcommon0 libwayland-client0 \
#     xdg-utils libu2f-udev libvulkan1 xvfb \
#     # Nettoyage
#     && rm -rf /var/lib/apt/lists/* \
#     && apt-get clean

# # Installation de Google Chrome
# RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
#     gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg && \
#     echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > \
#     /etc/apt/sources.list.d/google-chrome.list && \
#     apt-get update && \
#     apt-get install -y google-chrome-stable && \
#     rm -rf /var/lib/apt/lists/*

# # Installation de ChromeDriver
# RUN CHROMEDRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
#     python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") && \
#     echo "📥 Installation ChromeDriver version: $CHROMEDRIVER_VERSION" && \
#     curl -sSL "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
#     -o /tmp/chromedriver.zip && \
#     unzip /tmp/chromedriver.zip -d /tmp/ && \
#     mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
#     chmod +x /usr/local/bin/chromedriver && \
#     rm -rf /tmp/chromedriver* && \
#     echo "✅ ChromeDriver installé: $(chromedriver --version)"

# # Création de l'utilisateur airflow
# RUN groupadd -g ${AIRFLOW_GID} airflow && \
#     useradd -m -u ${AIRFLOW_UID} -g airflow -s /bin/bash airflow

# # # Mise à jour pip et installation d'Airflow
# # RUN pip install --upgrade pip setuptools wheel && \
# #     pip install "apache-airflow[celery,postgres,redis,crypto,ssh,ftp,http,ldap,kubernetes,docker]==${AIRFLOW_VERSION}" \
# #     --constraint "${CONSTRAINT_URL}"


# # Installer Airflow avec les contraintes officielles
# RUN pip install --upgrade pip setuptools wheel \
#     && pip install "apache-airflow[celery,postgres,redis]==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir --retries 5 --timeout 60 -r /tmp/requirements.txt && rm /tmp/requirements.txt


# # Copie et installation des requirements
# COPY requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
#     rm /tmp/requirements.txt

# # Installation des modèles SpaCy
# RUN python -m pip install \
#     https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.8.0/es_core_news_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-3.8.0/de_core_news_sm-3.8.0-py3-none-any.whl

# # Création des répertoires Airflow
# RUN mkdir -p ${AIRFLOW_HOME}/{dags,logs,plugins,config,scripts,data} \
#     ${AIRFLOW_HOME}/.dbt/{profiles,dbt_projects} \
#     ${AIRFLOW_HOME}/.cache && \
#     chown -R airflow:airflow ${AIRFLOW_HOME}

# # Script d'entrée personnalisé
# COPY --chown=airflow:airflow entrypoint.sh /entrypoint
# RUN chmod +x /entrypoint

# # Configuration pour Chrome headless
# ENV DISPLAY=:99
# ENV CHROME_BIN=/usr/bin/google-chrome
# ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# # Passage à l'utilisateur airflow
# USER airflow
# WORKDIR ${AIRFLOW_HOME}

# # Variables d'environnement pour l'utilisateur
# ENV PATH="${AIRFLOW_HOME}/.local/bin:$PATH"
# ENV PYTHONPATH="${AIRFLOW_HOME}:${PYTHONPATH}"

# # Ports exposés
# EXPOSE 8080 8793 5555

# # Healthcheck
# HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
#     CMD curl -f http://localhost:8080/health || exit 1

# # Point d'entrée
# ENTRYPOINT ["/entrypoint"]
# CMD ["airflow", "scheduler"]


# FROM apache/airflow:2.10.5-python3.11

# # Passer en root pour installer les paquets système + Google Chrome + ChromeDriver
# USER root

# # Dépendances système pour Chrome et ChromeDriver
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     bash curl wget gnupg unzip ca-certificates fonts-liberation \
#     libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
#     libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
#     libxdamage1 libxrandr2 xdg-utils libxshmfence1 libxfixes3 libxkbcommon0 \
#     libxrender1 libglib2.0-0 libpango-1.0-0 libpangocairo-1.0-0 libgtk-3-0 \
#     && rm -rf /var/lib/apt/lists/*

# # Ajouter clé + dépôt Google Chrome
# RUN mkdir -p /usr/share/keyrings && \
#     curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
#     gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg && \
#     echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
#     > /etc/apt/sources.list.d/google-chrome.list && \
#     apt-get update && \
#     apt-get install -y google-chrome-stable && \
#     rm -rf /var/lib/apt/lists/*

# # Télécharger et installer ChromeDriver compatible
# RUN CHROMEDRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
#     python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") && \
#     echo "📥 Installing ChromeDriver version: $CHROMEDRIVER_VERSION" && \
#     curl -sSL "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
#     -o /tmp/chromedriver.zip && \
#     unzip /tmp/chromedriver.zip -d /tmp/ && \
#     mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
#     chmod +x /usr/local/bin/chromedriver && \
#     rm -rf /tmp/chromedriver*

# # Revenir à l’utilisateur airflow pour la suite
# USER airflow

# # Créer un virtualenv
# RUN python -m venv /home/airflow/venv

# # Mettre à jour pip dans le virtualenv
# RUN /home/airflow/venv/bin/pip install --upgrade pip setuptools wheel

# # Copier les requirements
# USER root

# COPY requirements.txt /tmp/requirements.txt

# RUN /home/airflow/venv/bin/pip install \
#     --retries=10 \
#     --timeout=60 \
#     --no-cache-dir \
#     -r /tmp/requirements.txt && \
#     rm /tmp/requirements.txt

# USER airflow



# # Installer les modèles SpaCy multilingues dans le virtualenv
# RUN /home/airflow/venv/bin/pip install \
#     https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.8.0/es_core_news_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-3.8.0/de_core_news_sm-3.8.0-py3-none-any.whl

# # Config environnement pour Chrome headless
# ENV CHROME_BIN=/usr/bin/google-chrome
# ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# # Config virtualenv pour airflow
# ENV PATH="/home/airflow/venv/bin:$PATH"

# # Port exposé pour Airflow Web UI
# EXPOSE 8080

# # Dossier de travail
# WORKDIR $AIRFLOW_HOME

# FROM apache/airflow:2.10.5-python3.11

# USER root

# # Dépendances système pour Chrome et ChromeDriver
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     bash curl wget gnupg unzip ca-certificates fonts-liberation \
#     libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
#     libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
#     libxdamage1 libxrandr2 xdg-utils libxshmfence1 libxfixes3 libxkbcommon0 \
#     libxrender1 libglib2.0-0 libpango-1.0-0 libpangocairo-1.0-0 libgtk-3-0 \
#     && rm -rf /var/lib/apt/lists/*

# # Google Chrome
# RUN mkdir -p /usr/share/keyrings && \
#     curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
#     gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg && \
#     echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
#     > /etc/apt/sources.list.d/google-chrome.list && \
#     apt-get update && \
#     apt-get install -y google-chrome-stable && \
#     rm -rf /var/lib/apt/lists/*

# # ChromeDriver
# RUN CHROMEDRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
#     python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") && \
#     echo "📥 Installing ChromeDriver version: $CHROMEDRIVER_VERSION" && \
#     curl -sSL "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
#     -o /tmp/chromedriver.zip && \
#     unzip /tmp/chromedriver.zip -d /tmp/ && \
#     mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
#     chmod +x /usr/local/bin/chromedriver && \
#     rm -rf /tmp/chromedriver*

# # Virtualenv
# USER airflow
# RUN python -m venv /home/airflow/venv

# # Upgrade pip etc.
# RUN /home/airflow/venv/bin/pip install --upgrade pip setuptools wheel

# # Repasser root pour COPY + install
# USER root
# COPY requirements.txt /tmp/requirements.txt

# RUN /home/airflow/venv/bin/pip install \
#     --retries=10 \
#     --timeout=60 \
#     --no-cache-dir \
#     -r /tmp/requirements.txt && \
#     rm -f /tmp/requirements.txt

# # Installer SpaCy models
# RUN /home/airflow/venv/bin/pip install \
#     https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.8.0/es_core_news_sm-3.8.0-py3-none-any.whl \
#     https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-3.8.0/de_core_news_sm-3.8.0-py3-none-any.whl

# # Config environnement
# ENV CHROME_BIN=/usr/bin/google-chrome
# ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
# ENV PATH="/home/airflow/venv/bin:$PATH"

# EXPOSE 8080

# WORKDIR $AIRFLOW_HOME

# USER airflow

FROM apache/airflow:2.10.5-python3.11

USER root

# Dépendances système pour Chrome et ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl wget gnupg unzip ca-certificates fonts-liberation \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils libxshmfence1 libxfixes3 libxkbcommon0 \
    libxrender1 libglib2.0-0 libpango-1.0-0 libpangocairo-1.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Google Chrome
RUN mkdir -p /usr/share/keyrings && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['channels']['Stable']['version'])") && \
    echo "📥 Installing ChromeDriver version: $CHROMEDRIVER_VERSION" && \
    curl -sSL "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    -o /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

# Création du virtualenv
USER airflow
RUN python -m venv /home/airflow/venv
ENV PATH="/home/airflow/venv/bin:$PATH"

# Upgrade pip etc.
RUN pip install --upgrade pip setuptools wheel

USER root
COPY requirements.txt /tmp/requirements.txt

RUN /home/airflow/venv/bin/pip install \
    --retries=10 \
    --timeout=60 \
    --no-cache-dir \
    -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

# Installer modèles SpaCy
RUN /home/airflow/venv/bin/pip install \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl \
    https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl \
    https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.8.0/es_core_news_sm-3.8.0-py3-none-any.whl \
    https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-3.8.0/de_core_news_sm-3.8.0-py3-none-any.whl

# Configuration ENV
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV PYTHONPATH="/home/airflow/venv/lib/python3.11/site-packages"
ENV PATH="/home/airflow/venv/bin:$PATH"

EXPOSE 8080

WORKDIR $AIRFLOW_HOME

USER airflow

