.PHONY: help install install-dev test test-cov lint format type-check security build clean all ci pr-check
.DEFAULT_GOAL := help

# Colors for output
CYAN = \033[0;36m
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)CMMN Parser - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(CYAN)Quick Start:$(NC)"
	@echo "  make install-dev  # Install development dependencies"
	@echo "  make ci          # Run all CI checks (like GitHub Actions)"
	@echo "  make test        # Run tests only"

install: ## Install production dependencies
	@echo "$(CYAN)Installing production dependencies...$(NC)"
	uv sync

install-dev: ## Install development dependencies
	@echo "$(CYAN)Installing development dependencies...$(NC)"
	uv sync --extra dev --extra test

test: ## Run tests
	@echo "$(CYAN)Running tests...$(NC)"
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "$(CYAN)Running tests with coverage...$(NC)"
	uv run pytest tests/ -v --cov=src/cmmn_parser --cov-report=term --cov-report=html

test-cov-xml: ## Run tests with XML coverage report (for CI)
	@echo "$(CYAN)Running tests with XML coverage...$(NC)"
	uv run pytest tests/ -v --cov=src/cmmn_parser --cov-report=xml --cov-report=term

lint: ## Run linting (flake8)
	@echo "$(CYAN)Running flake8 linting...$(NC)"
	@echo "$(YELLOW)Checking for syntax errors and undefined names...$(NC)"
	uv run flake8 src/cmmn_parser --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "$(YELLOW)Running full linting...$(NC)"
	uv run flake8 src/cmmn_parser --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code (black + isort)
	@echo "$(CYAN)Formatting code with black...$(NC)"
	uv run black src/cmmn_parser tests/
	@echo "$(CYAN)Sorting imports with isort...$(NC)"
	uv run isort src/cmmn_parser tests/

format-check: ## Check if code is properly formatted
	@echo "$(CYAN)Checking code formatting...$(NC)"
	uv run black --check src/cmmn_parser tests/
	uv run isort --check-only src/cmmn_parser tests/

type-check: ## Run type checking (mypy)
	@echo "$(CYAN)Running mypy type checking...$(NC)"
	uv run mypy src/cmmn_parser --ignore-missing-imports

security: ## Run security checks
	@echo "$(CYAN)Running security checks...$(NC)"
	uv pip install safety
	uv run safety check --json || true

build: ## Build the package
	@echo "$(CYAN)Building package...$(NC)"
	uv build

build-test: ## Test the built package
	@echo "$(CYAN)Testing package installation...$(NC)"
	uv pip install dist/*.whl
	python -c "import cmmn_parser; print('Package imported successfully')"
	python -c "from cmmn_parser import CMMNParser, parse_cmmn_string; print('Parser functions work')"

clean: ## Clean build artifacts and cache
	@echo "$(CYAN)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean ## Clean everything including virtual environment
	@echo "$(CYAN)Cleaning virtual environment...$(NC)"
	rm -rf .venv/

# Combined targets
all: format lint type-check test-cov ## Run formatting, linting, type-checking, and tests

ci: format-check lint type-check test-cov-xml ## Run all CI checks (mirrors GitHub Actions)
	@echo "$(GREEN)✅ All CI checks passed!$(NC)"

pr-check: ## Run quick PR checks
	@echo "$(CYAN)Running PR validation checks...$(NC)"
	@echo "$(YELLOW)Running quick tests...$(NC)"
	uv run pytest tests/test_models.py -v
	@echo "$(YELLOW)Checking formatting...$(NC)"
	uv run black --check src/cmmn_parser tests/
	uv run isort --check-only src/cmmn_parser tests/
	@echo "$(GREEN)✅ PR checks passed!$(NC)"

dev-setup: install-dev ## Set up development environment
	@echo "$(CYAN)Setting up development environment...$(NC)"
	@echo "$(GREEN)✅ Development environment ready!$(NC)"
	@echo ""
	@echo "$(CYAN)Next steps:$(NC)"
	@echo "  make test        # Run tests"
	@echo "  make ci          # Run full CI suite"
	@echo "  make format      # Format code"

# Example/demo targets
example: ## Run the example script
	@echo "$(CYAN)Running example script...$(NC)"
	uv run python example.py

demo: install example ## Install and run demo
	@echo "$(GREEN)✅ Demo completed!$(NC)"

# Release helpers
pre-release: ci build build-test ## Run all pre-release checks
	@echo "$(GREEN)✅ Ready for release!$(NC)"

release-check: ## Check if ready for release
	@echo "$(CYAN)Checking release readiness...$(NC)"
	@echo "$(YELLOW)Checking if working directory is clean...$(NC)"
	@git diff-index --quiet HEAD -- || (echo "$(RED)❌ Working directory not clean$(NC)" && exit 1)
	@echo "$(YELLOW)Checking test coverage...$(NC)"
	@$(MAKE) test-cov-xml
	@echo "$(GREEN)✅ Ready for release!$(NC)"

# Development workflow helpers
watch-test: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(CYAN)Installing pytest-watch and running tests in watch mode...$(NC)"
	uv pip install pytest-watch
	uv run ptw tests/

quick: ## Quick development check (format + test models only)
	@echo "$(CYAN)Running quick development check...$(NC)"
	$(MAKE) format
	uv run pytest tests/test_models.py -v
	@echo "$(GREEN)✅ Quick check completed!$(NC)"

# Documentation helpers
docs-deps: ## Install documentation dependencies (if needed in future)
	@echo "$(CYAN)Documentation dependencies not yet configured$(NC)"

# Git hooks simulation
pre-commit: format-check lint type-check ## Simulate pre-commit hooks
	@echo "$(GREEN)✅ Pre-commit checks passed!$(NC)"

# Performance/benchmark (placeholder for future)
benchmark: ## Run performance benchmarks (placeholder)
	@echo "$(YELLOW)Benchmarking not yet implemented$(NC)"

# Database of available Python versions for testing
python-versions: ## Show supported Python versions
	@echo "$(CYAN)Supported Python versions:$(NC)"
	@echo "  - Python 3.8"
	@echo "  - Python 3.9"
	@echo "  - Python 3.10"
	@echo "  - Python 3.11"
	@echo "  - Python 3.12"
	@echo "  - Python 3.13"

# Check tool versions
versions: ## Show versions of tools
	@echo "$(CYAN)Tool versions:$(NC)"
	@echo "Python: $$(python --version 2>/dev/null || echo 'Not available')"
	@echo "uv: $$(uv --version 2>/dev/null || echo 'Not available')"
	@echo "pytest: $$(uv run pytest --version 2>/dev/null | head -1 || echo 'Not available')"
	@echo "black: $$(uv run black --version 2>/dev/null || echo 'Not available')"
	@echo "mypy: $$(uv run mypy --version 2>/dev/null || echo 'Not available')"
	@echo "flake8: $$(uv run flake8 --version 2>/dev/null || echo 'Not available')"