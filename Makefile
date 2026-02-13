# Makefile for schemas-demo project
# Uses uv as the package manager

.PHONY: help setup install install-dev sync update proto run dev test test-cov test-watch lint format check pre-commit type-check clean docker docker-up docker-down examples clients all

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(BLUE)Available commands:$(NC)'
	@echo ''
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''
	@echo '$(YELLOW)Quick start:$(NC)'
	@echo '  make setup     # Initial setup (run once)'
	@echo '  make proto     # Generate Protobuf code'
	@echo '  make dev       # Start development server'
	@echo '  make test      # Run tests'

# =============================================================================
# Setup and Installation
# =============================================================================

setup: ## Complete project setup (run this first)
	@echo "$(BLUE)Setting up schemas-demo project...$(NC)"
	@command -v uv >/dev/null 2>&1 || { echo "$(RED)Error: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh$(NC)"; exit 1; }
	@echo "$(GREEN)✓ uv is installed$(NC)"
	uv venv
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	uv pip install -e .
	@echo "$(GREEN)✓ Dependencies installed$(NC)"
	@if [ ! -f .env ]; then cp .env.example .env && echo "$(GREEN)✓ Created .env file$(NC)"; else echo "$(YELLOW)! .env already exists$(NC)"; fi
	@echo "$(BLUE)Setup complete! Next steps:$(NC)"
	@echo "  1. Edit .env with your information"
	@echo "  2. Run: make proto"
	@echo "  3. Run: make dev"

install: ## Install production dependencies with uv
	uv pip install -e .

install-dev: ## Install with development dependencies
	uv pip install -e ".[dev]"

sync: ## Sync dependencies from pyproject.toml
	uv pip sync

update: ## Update all dependencies to latest versions
	uv pip install --upgrade -e ".[dev]"

# =============================================================================
# Protobuf Code Generation
# =============================================================================

proto: ## Generate Python code from Protobuf schema
	@echo "$(BLUE)Generating Protobuf code...$(NC)"
	@command -v protoc >/dev/null 2>&1 || { echo "$(RED)Error: protoc not found. Install: brew install protobuf (macOS) or apt-get install protobuf-compiler (Linux)$(NC)"; exit 1; }
	protoc --python_out=. --pyi_out=. schemas/user.proto
	@echo "$(GREEN)✓ Generated schemas/user_pb2.py and schemas/user_pb2.pyi$(NC)"

proto-clean: ## Remove generated Protobuf files
	find . -type f -name "*_pb2.py" -delete
	find . -type f -name "*_pb2.pyi" -delete

# =============================================================================
# Development Server
# =============================================================================

run: ## Run the FastAPI development server
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev: run ## Alias for 'make run'

run-prod: ## Run production server (no reload)
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# =============================================================================
# Testing
# =============================================================================

test: ## Run all tests
	uv run pytest -v

test-cov: ## Run tests with coverage report
	uv run pytest -v --cov=app --cov-report=html --cov-report=term --cov-report=xml

test-watch: ## Run tests in watch mode (requires pytest-watch)
	uv run ptw -- -v

test-fast: ## Run tests without coverage (faster)
	uv run pytest -v -x

test-failed: ## Re-run only failed tests
	uv run pytest -v --lf

test-verbose: ## Run tests with verbose output
	uv run pytest -vv -s

test-json: ## Run only JSON endpoint tests
	uv run pytest -v tests/test_json_endpoint.py

test-avro: ## Run only Avro endpoint tests
	uv run pytest -v tests/test_avro_endpoint.py

test-protobuf: ## Run only Protobuf endpoint tests
	uv run pytest -v tests/test_protobuf_endpoint.py

# =============================================================================
# Code Quality
# =============================================================================

pre-commit: ## Run all pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	@command -v pre-commit >/dev/null 2>&1 || { echo "$(RED)Error: pre-commit not found. Run: pip install pre-commit$(NC)"; exit 1; }
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit hooks completed$(NC)"

lint: ## Run all linters (flake8, mypy)
	@echo "$(BLUE)Running flake8...$(NC)"
	uv run flake8 app tests examples clients
	@echo "$(BLUE)Running mypy...$(NC)"
	uv run mypy app

format: ## Format code with black and isort
	@echo "$(BLUE)Running black...$(NC)"
	uv run black app tests examples clients
	@echo "$(BLUE)Running isort...$(NC)"
	uv run isort app tests examples clients

format-check: ## Check code formatting without modifying
	uv run black --check app tests examples clients
	uv run isort --check-only app tests examples clients

type-check: ## Run type checking with mypy
	uv run mypy app

check: format-check lint type-check ## Run all checks (format, lint, type)

# =============================================================================
# Examples and Clients
# =============================================================================

examples: ## Run all standalone examples
	@echo "$(BLUE)Running Avro example...$(NC)"
	uv run python examples/avro_example.py
	@echo ""
	@echo "$(BLUE)Running JSON Schema example...$(NC)"
	uv run python examples/jsonschema_example.py
	@echo ""
	@if [ -f schemas/user_pb2.py ]; then \
		echo "$(BLUE)Running Protobuf example...$(NC)"; \
		uv run python examples/protobuf_example.py; \
	else \
		echo "$(YELLOW)Skipping Protobuf example (run 'make proto' first)$(NC)"; \
	fi

example-avro: ## Run Avro example only
	uv run python examples/avro_example.py

example-json: ## Run JSON Schema example only
	uv run python examples/jsonschema_example.py

example-protobuf: ## Run Protobuf example only
	uv run python examples/protobuf_example.py

clients: ## Test all API endpoints (requires server running)
	@echo "$(YELLOW)Make sure the server is running: make dev$(NC)"
	@echo ""
	@echo "$(BLUE)Testing JSON endpoint...$(NC)"
	./clients/test_json_endpoint.sh
	@echo ""
	@echo "$(BLUE)Testing Avro endpoint...$(NC)"
	uv run python clients/test_avro_endpoint.py
	@echo ""
	@if [ -f schemas/user_pb2.py ]; then \
		echo "$(BLUE)Testing Protobuf endpoint...$(NC)"; \
		uv run python clients/test_protobuf_endpoint.py; \
	else \
		echo "$(YELLOW)Skipping Protobuf test (run 'make proto' first)$(NC)"; \
	fi

# =============================================================================
# Docker
# =============================================================================

docker: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t schemas-demo:latest .
	@echo "$(GREEN)✓ Docker image built: schemas-demo:latest$(NC)"

docker-up: ## Start Docker containers with docker-compose
	docker-compose up --build

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker container logs
	docker-compose logs -f

docker-shell: ## Open shell in running container
	docker exec -it schemas-demo-api /bin/bash

# =============================================================================
# Cleanup
# =============================================================================

clean: ## Clean generated files and caches
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-proto: proto-clean ## Alias for proto-clean

clean-all: clean proto-clean ## Clean everything including Protobuf files
	rm -rf .venv
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

# =============================================================================
# CI/CD
# =============================================================================

ci: check test-cov ## Run all CI checks (format, lint, type, tests with coverage)
	@echo "$(GREEN)✓ All CI checks passed$(NC)"

# =============================================================================
# Information
# =============================================================================

info: ## Show project information
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Name:         schemas-demo"
	@echo "  Version:      0.1.0"
	@echo "  Python:       $$(uv run python --version)"
	@echo "  uv:           $$(uv --version)"
	@echo "  Virtual env:  $$([ -d .venv ] && echo 'Present' || echo 'Not created')"
	@echo "  .env:         $$([ -f .env ] && echo 'Present' || echo 'Not found')"
	@echo "  Protobuf:     $$([ -f schemas/user_pb2.py ] && echo 'Generated' || echo 'Not generated (run make proto)')"
	@echo ""
	@echo "$(BLUE)Endpoints:$(NC)"
	@echo "  JSON:         POST http://localhost:8000/json/user"
	@echo "  Protobuf:     POST http://localhost:8000/protobuf/user"
	@echo "  Avro:         POST http://localhost:8000/avro/user"
	@echo "  Docs:         http://localhost:8000/docs"
	@echo "  Health:       http://localhost:8000/health"

deps: ## Show installed dependencies
	uv pip list

tree: ## Show project tree structure
	@command -v tree >/dev/null 2>&1 && tree -I '__pycache__|*.pyc|.venv|.pytest_cache|.mypy_cache|htmlcov' -L 3 || echo "tree command not found"

# =============================================================================
# Convenience
# =============================================================================

all: setup proto dev ## Setup, generate proto, and start dev server

.DEFAULT_GOAL := help
