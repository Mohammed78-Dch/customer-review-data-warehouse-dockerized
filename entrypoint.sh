# #!/bin/bash
# set -e

# # Function to wait for service
# wait_for_service() {
#     local host=$1
#     local port=$2
#     local service_name=$3
    
#     echo "Waiting for $service_name to be ready..."
#     while ! nc -z $host $port; do
#         sleep 1
#     done
#     echo "$service_name is ready!"
# }

# # Wait for PostgreSQL
# if [[ "${1}" != "version" ]]; then
#     wait_for_service postgres 5432 "PostgreSQL"
# fi

# # Wait for Redis (only for worker and scheduler)
# if [[ "${1}" == "celery" ]] || [[ "${1}" == "scheduler" ]] || [[ "${1}" == "worker" ]]; then
#     wait_for_service redis 6379 "Redis"
# fi

# # Handle different command formats
# case "${1}" in
#     webserver|scheduler|worker|triggerer)
#         exec airflow "${@}"
#         ;;
#     celery)
#         if [[ "${2}" == "worker" ]]; then
#             exec airflow celery worker
#         elif [[ "${2}" == "flower" ]]; then
#             exec airflow celery flower
#         else
#             exec airflow "${@}"
#         fi
#         ;;
#     version)
#         exec airflow version
#         ;;
#     bash)
#         exec /bin/bash
#         ;;
#     *)
#         # If it starts with airflow, execute as-is
#         if [[ "${1}" == "airflow" ]]; then
#             exec "${@}"
#         else
#             # Otherwise, prepend airflow
#             exec airflow "${@}"
#         fi
#         ;;
# esac

#!/bin/bash
set -euo pipefail

# Colors pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Fonction pour attendre qu'un service soit disponible
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    log_info "Attente de $service_name ($host:$port)..."
    
    while ! nc -z "$host" "$port" >/dev/null 2>&1; do
        if [ $attempt -eq $max_attempts ]; then
            log_error "Impossible de se connecter à $service_name après $max_attempts tentatives"
            exit 1
        fi
        
        log_warn "Tentative $attempt/$max_attempts - $service_name non disponible, nouvelle tentative dans 2s..."
        sleep 2
        ((attempt++))
    done
    
    log_success "$service_name est disponible!"
}

# Fonction pour initialiser la base de données
init_database() {
    if [[ "${_AIRFLOW_DB_MIGRATE:-}" == "true" ]]; then
        log_info "Migration de la base de données Airflow..."
        airflow db migrate
        log_success "Migration terminée"
    fi
}

# Fonction pour créer l'utilisateur admin
create_admin_user() {
    if [[ "${_AIRFLOW_WWW_USER_CREATE:-}" == "true" ]]; then
        local username="${_AIRFLOW_WWW_USER_USERNAME:-admin}"
        local password="${_AIRFLOW_WWW_USER_PASSWORD:-admin}"
        
        log_info "Création de l'utilisateur admin: $username"
        
        airflow users create \
            --username "$username" \
            --firstname "Admin" \
            --lastname "User" \
            --role "Admin" \
            --email "admin@example.com" \
            --password "$password" 2>/dev/null || {
                log_warn "L'utilisateur admin existe déjà ou erreur lors de la création"
            }
    fi
}

# Fonction pour configurer Chrome
setup_chrome() {
    log_info "Configuration de Chrome pour Selenium..."
    
    # Vérification de Chrome
    if command -v google-chrome >/dev/null 2>&1; then
        CHROME_VERSION=$(google-chrome --version)
        log_success "Chrome installé: $CHROME_VERSION"
    else
        log_error "Chrome non trouvé"
        exit 1
    fi
    
    # Vérification de ChromeDriver
    if command -v chromedriver >/dev/null 2>&1; then
        CHROMEDRIVER_VERSION=$(chromedriver --version)
        log_success "ChromeDriver installé: $CHROMEDRIVER_VERSION"
    else
        log_error "ChromeDriver non trouvé"
        exit 1
    fi
    
    # Configuration Xvfb pour mode headless
    if command -v Xvfb >/dev/null 2>&1; then
        log_info "Démarrage de Xvfb pour le mode headless..."
        Xvfb :99 -screen 0 1920x1080x24 >/dev/null 2>&1 &
        export DISPLAY=:99
        log_success "Xvfb démarré sur DISPLAY=:99"
    fi
}

# Fonction pour configurer dbt
setup_dbt() {
    log_info "Configuration de dbt..."
    
    # Création du répertoire profiles dbt
    mkdir -p "${AIRFLOW_HOME}/.dbt"
    
    # Configuration des permissions
    chmod 755 "${AIRFLOW_HOME}/.dbt"
    
    if [ -f "${AIRFLOW_HOME}/.dbt/profiles.yml" ]; then
        log_success "Profil dbt trouvé"
    else
        log_warn "Aucun profil dbt trouvé - créez ${AIRFLOW_HOME}/.dbt/profiles.yml"
    fi
}

# Fonction pour installer les dépendances additionnelles
install_additional_requirements() {
    if [[ -n "${_PIP_ADDITIONAL_REQUIREMENTS:-}" ]]; then
        log_info "Installation des dépendances supplémentaires: $_PIP_ADDITIONAL_REQUIREMENTS"
        pip install $_PIP_ADDITIONAL_REQUIREMENTS
        log_success "Dépendances supplémentaires installées"
    fi
}

# Fonction principale
main() {
    log_info "🚀 Démarrage d'Airflow..."
    log_info "Commande: $*"
    
    # Installation des dépendances supplémentaires
    install_additional_requirements
    
    # Configuration de Chrome
    setup_chrome
    
    # Configuration de dbt
    setup_dbt
    
    # Attendre les services de base pour certaines commandes
    case "${1:-}" in
        webserver|scheduler|worker|triggerer|flower)
            wait_for_service postgres 5432 "PostgreSQL"
            wait_for_service redis 6379 "Redis"
            ;;
        *)
            log_info "Mode commande directe - pas d'attente des services"
            ;;
    esac
    
    # Initialisation de la base de données si nécessaire
    init_database
    
    # Création de l'utilisateur admin si nécessaire
    create_admin_user
    
    # Vérification de la configuration Airflow
    log_info "Vérification de la configuration Airflow..."
    airflow config list >/dev/null 2>&1 && log_success "Configuration Airflow OK"
    
    # Affichage de la commande qui va être exécutée
    log_success "Lancement de: $*"
    
    # Exécution de la commande
    exec "$@"
}

# Gestion des signaux pour un arrêt propre
trap 'log_warn "Signal reçu, arrêt en cours..."; exit 0' SIGTERM SIGINT

# Exécution du script principal
main "$@"