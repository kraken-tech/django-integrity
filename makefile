SHELL=/bin/bash

.PHONY:help
help:
	@echo "Available targets:"
	@echo "  help: Show this help message"
	@echo "  install: Install dev dependencies"
	@echo "  update: Update dev dependencies"
	@echo "  test: Run Python tests"
	@echo "  lint: Run formatters and static analysis checks"


# Standard entry points
# =====================

.PHONY:install
install: install_python_packages

.PHONY:test
test:
	tox --parallel
	./scripts/type-ratchet.py check

.PHONY:lint
lint: format style typing

.PHONY:update
update:
	pip-compile pyproject.toml --quiet --upgrade --resolver=backtracking --extra=dev --output-file=requirements/development.txt --unsafe-package django


# Implementation details
# ======================

# Pip install all required Python packages
.PHONY:install_python_packages
install_python_packages: install_prerequisites requirements/development.txt
	pip-sync requirements/development.txt

.PHONY:install_prerequisites
install_prerequisites: requirements/prerequisites.txt
	pip install --quiet --requirement requirements/prerequisites.txt

# Add new dependencies to requirements/development.txt whenever pyproject.toml changes
requirements/development.txt: pyproject.toml
	pip-compile pyproject.toml --quiet --resolver=backtracking --extra=dev --output-file=requirements/development.txt --unsafe-package django

.PHONY:format
format:
	ruff format --check .

.PHONY:style
style:
	ruff check --fix .

.PHONY:typing
typing:
	./scripts/type-ratchet.py update
