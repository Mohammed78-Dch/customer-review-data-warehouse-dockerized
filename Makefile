# ===============================================
# Makefile pour projet Airflow Data Warehouse
# ===============================================

# Variables
DOCKER_COMPOSE = docker-compose
AIRFLOW_UID = $(shell id -u)
PROJECT_NAME = airflow-dwh

# Couleurs pour les messages
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help build up down restart logs clean init test lint format

# Commande par défaut
help: ## Affiche l'aide
	@echo "$(BLUE)=== Airflow Data Warehouse - Commandes disponibles ===$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ===============================================
# Commandes Docker
# ===============================================

build: ## Construire les images Docker
	@echo "$(BLUE)🔨 Construction des images Docker...$(NC)"
	AIRFLOW_UID=$(AIRFLOW_UID) $(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Images construites avec succès$(NC)"

up: ## Démarrer tous les services
	@echo "$(BLUE)🚀 Démarrage des services Airflow...$(NC)"
	AIRFLOW_UID=$(AIRFLOW_UID) $(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Services démarrés$(NC)"
	@echo "$(YELLOW)🌐 Interface web: http://localhost:8080$(NC)"
	@echo "$(YELLOW)👤 Login: admin / admin$(NC)"

down: ## Arrêter tous les services
	@echo "$(BLUE)🛑 Arrêt des services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Services arrêtés$(NC)"

stop: ## Arrêter les services sans supprimer les conteneurs
	@echo "$(BLUE)⏸️  Arrêt des services...$(NC)"
	$(DOCKER_COMPOSE) stop
	@echo "$(GREEN)✅ Services en pause$(NC)"

restart: ## Redémarrer tous les services
	@echo "$(BLUE)🔄 Redémarrage des services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ Services redémarrés$(NC)"

# ===============================================
# Commandes de développement
# ===============================================

init: ## Initialiser le projet (première utilisation)
	@echo "$(BLUE)🎯 Initialisation du projet...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)📝 Création du fichier .env...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✅ Fichier .env créé$(NC)"; \
	fi
	@mkdir -p dags logs plugins config scripts data dbt_projects .dbt/profiles
	@echo "$(GREEN)✅ Structure de dossiers créée$(NC)"
	@echo "$(BLUE)🔨 Construction et démarrage...$(NC)"
	$(MAKE) build
	$(MAKE) up
	@echo "$(GREEN)🎉 Projet initialisé avec succès !$(NC)"

clean: ## Nettoyer les volumes et images
	@echo "$(BLUE)🧹 Nettoyage...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

clean-all: ## Nettoyage complet (ATTENTION: supprime tout)
	@echo "$(RED)⚠️  ATTENTION: Suppression complète des données !$(NC)"
	@read -p "Êtes-vous sûr ? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -af
	docker volume prune -f
	@echo "$(GREEN)✅ Nettoyage complet terminé$(NC)"

# ===============================================
# Commandes de monitoring
# ===============================================

logs: ## Afficher les logs de tous les services
	$(DOCKER_COMPOSE) logs -f

logs-web: ## Logs du webserver uniquement
	$(DOCKER_COMPOSE) logs -f airflow-webserver

logs-scheduler: ## Logs du scheduler uniquement
	$(DOCKER_COMPOSE) logs -f airflow-scheduler

logs-worker: ## Logs des workers uniquement
	$(DOCKER_COMPOSE) logs -f airflow-worker

ps: ## Statut des services
	@echo "$(BLUE)📊 Statut des services:$(NC)"
	$(DOCKER_COMPOSE) ps

stats: ## Statistiques des conteneurs
	@echo "$(BLUE)📈 Statistiques des conteneurs:$(NC)"
	docker stats $$($(DOCKER_COMPOSE) ps -q)

# ===============================================
# Commandes Airflow
# ===============================================

cli: ## Ouvrir un shell dans le conteneur Airflow
	@echo "$(BLUE)🖥️  Ouverture du shell Airflow...$(NC)"
	$(DOCKER_COMPOSE) exec airflow-webserver bash

db-reset: ## Réinitialiser la base de données Airflow
	@echo "$(RED)⚠️  ATTENTION: Réinitialisation de la base de données !$(NC)"
	@read -p "Êtes-vous sûr ? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(DOCKER_COMPOSE) exec airflow-webserver airflow db reset -y
	@echo "$(GREEN)✅ Base de données réinitialisée$(NC)"

user-create: ## Créer un nouvel utilisateur admin
	@echo "$(BLUE)👤 Création d'un utilisateur admin...$(NC)"
	@read -p "Nom d'utilisateur: " username; \
	read -s -p "Mot de passe: " password; \
	echo; \
	$(DOCKER_COMPOSE) exec airflow-webserver airflow users create \
		--username "$$username" \
		--firstname "Admin" \
		--lastname "User" \
		--role "Admin" \
		--email "admin@example.com" \
		--password "$$password"

dags-list: ## Lister tous les DAGs
	$(DOCKER_COMPOSE) exec airflow-webserver airflow dags list

dags-trigger: ## Déclencher un DAG manuellement
	@read -p "Nom du DAG: " dag_id; \
	$(DOCKER_COMPOSE) exec airflow-webserver airflow dags trigger "$$dag_id"

# ===============================================
# Commandes dbt
# ===============================================

dbt-init: ## Initialiser un nouveau projet dbt
	@read -p "Nom du projet dbt: " project_name; \
	$(DOCKER_COMPOSE) exec airflow-webserver dbt init "$$project_name" --profiles-dir /opt/airflow/.dbt

dbt-debug: ## Vérifier la configuration dbt
	$(DOCKER_COMPOSE) exec airflow-webserver dbt debug --profiles-dir /opt/airflow/.dbt

dbt-run: ## Exécuter les modèles dbt
	@read -p "Nom du projet dbt: " project_name; \
	$(DOCKER_COMPOSE) exec airflow-webserver dbt run --project-dir /opt/airflow/dbt_projects/"$$project_name" --profiles-dir /opt/airflow/.dbt

dbt-test: ## Exécuter les tests dbt
	@read -p "Nom du projet dbt: " project_name; \
	$(DOCKER_COMPOSE) exec airflow-webserver dbt test --project-dir /opt/airflow/dbt_projects/"$$project_name" --profiles-dir /opt/airflow/.dbt

# ===============================================
# Commandes de développement et tests
# ===============================================

test: ## Exécuter les tests
	@echo "$(BLUE)🧪 Exécution des tests...$(NC)"
	$(DOCKER_COMPOSE) exec airflow-webserver python -m pytest tests/ -v
	@echo "$(GREEN)✅ Tests terminés$(NC)"

lint: ## Vérifier le code avec flake8
	@echo "$(BLUE)🔍 Vérification du code...$(NC)"
	$(DOCKER_COMPOSE) exec airflow-webserver flake8 dags/ plugins/ --max-line-length=88 --extend-ignore=E203,W503

format: ## Formater le code avec black
	@echo "$(BLUE)🎨 Formatage du code...$(NC)"
	$(DOCKER_COMPOSE) exec airflow-webserver black dags/ plugins/ --line-length=88
	@echo "$(GREEN)✅ Code formaté$(NC)"

# ===============================================
# Commandes de sauvegarde
# ===============================================

backup-db: ## Sauvegarder la base de données
	@echo "$(BLUE)💾 Sauvegarde de la base de données...$(NC)"
	mkdir -p backups
	$(DOCKER_COMPOSE) exec postgres pg_dump -U airflow -d airflow > backups/airflow_db_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Sauvegarde créée dans backups/$(NC)"

restore-db: ## Restaurer la base de données
	@echo "$(RED)⚠️  ATTENTION: Restauration de la base de données !$(NC)"
	@ls -la backups/*.sql
	@read -p "Nom du fichier de sauvegarde: " backup_file; \
	$(DOCKER_COMPOSE) exec -T postgres psql -U airflow -d airflow < "$$backup_file"

# ===============================================
# Commandes de monitoring avancé
# ===============================================

flower: ## Démarrer Flower (monitoring Celery)
	@echo "$(BLUE)🌸 Démarrage de Flower...$(NC)"
	$(DOCKER_COMPOSE) --profile flower up -d flower
	@echo "$(GREEN)✅ Flower démarré: http://localhost:5555$(NC)"

debug: ## Démarrer en mode debug
	@echo "$(BLUE)🐛 Mode debug activé...$(NC)"
	$(DOCKER_COMPOSE) --profile debug run --rm airflow-cli

# ===============================================
# Commandes utilitaires
# ===============================================

env: ## Afficher les variables d'environnement
	@echo "$(BLUE)🔧 Variables d'environnement:$(NC)"
	@echo "AIRFLOW_UID: $(AIRFLOW_UID)"
	@echo "PROJECT_NAME: $(PROJECT_NAME)"

urls: ## Afficher les URLs importantes
	@echo "$(BLUE)🌐 URLs disponibles:$(NC)"
	@echo "$(GREEN)Airflow Web UI:$(NC) http://localhost:8080"
	@echo "$(GREEN)Flower (Celery):$(NC) http://localhost:5555 (avec --profile flower)"
	@echo "$(GREEN)PostgreSQL:$(NC) localhost:5432"

update: ## Mettre à jour les images Docker
	@echo "$(BLUE)⬆️  Mise à jour des images...$(NC)"
	$(DOCKER_COMPOSE) pull
	$(MAKE) build
	@echo "$(GREEN)✅ Images mises à jour$(NC)"