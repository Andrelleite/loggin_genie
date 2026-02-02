# Makefile for Loggin Genie

.PHONY: help install dev build up down logs clean test

help: ## Show this help message
	@echo '🧞‍♂️ Loggin Genie - Available Commands:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

install-api: ## Install API dependencies
	cd api && npm install

dev: ## Run in development mode
	@echo "Starting development servers..."
	cd api && npm run dev &
	python loggin_genie.py --help

build: ## Build Docker containers
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "   Web UI: http://localhost:8080"
	@echo "   API: http://localhost:3000"
	@echo "   Health: http://localhost:3000/health"

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

logs-api: ## View API logs
	docker-compose logs -f api

logs-python: ## View Python worker logs
	docker-compose logs -f python-worker

restart: ## Restart services
	docker-compose restart

ps: ## Show running containers
	docker-compose ps

test: ## Run tests
	python examples/test_decryption.py

test-api: ## Test API health
	curl http://localhost:3000/health

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf uploads/* output/*

rebuild: ## Rebuild and restart
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

shell-api: ## Open shell in API container
	docker exec -it loggin-genie-api sh

shell-python: ## Open shell in Python container
	docker exec -it loggin-genie-python bash

stats: ## Show container stats
	docker stats

backup: ## Backup data
	mkdir -p backup
	docker cp loggin-genie-api:/app/output ./backup/
	docker cp loggin-genie-api:/app/uploads ./backup/
	@echo "✅ Backup created in ./backup/"

restore: ## Restore data from backup
	docker cp ./backup/output loggin-genie-api:/app/
	docker cp ./backup/uploads loggin-genie-api:/app/
	@echo "✅ Data restored!"
