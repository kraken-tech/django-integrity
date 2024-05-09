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
install: install_python_packages install_pre_commit

.PHONY:test
test:
	tox --parallel
	./scripts/type-ratchet.py check

.PHONY:lint
lint: format style typing

.PHONY:update
update:
	pip-compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=dev \
		--output-file=requirements/development.txt
	pip-compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=pytest-in-tox \
		--output-file=requirements/pytest-in-tox.txt \
		--unsafe-package django
	pip-compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=release \
		--output-file=requirements/release.txt
	pip-compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=tox \
		--output-file=requirements/tox.txt


# Implementation details
# ======================

# Pip install all required Python packages
.PHONY:install_python_packages
install_python_packages: install_prerequisites requirements/development.txt
	pip-sync requirements/development.txt

.PHONY:install_prerequisites
install_prerequisites: requirements/prerequisites.txt
	pip install --quiet --requirement requirements/prerequisites.txt

.PHONY:install_pre_commit
install_pre_commit:
	pre-commit install

# Add new dependencies to requirements/development.txt whenever pyproject.toml changes
requirements/development.txt: pyproject.toml
	pip-compile pyproject.toml \
		--quiet --resolver=backtracking --strip-extras \
		--extra=dev \
		--output-file=requirements/development.txt

.PHONY:format
format:
	ruff format --check .

.PHONY:style
style:
	ruff check --fix .

.PHONY:typing
typing:
	./scripts/type-ratchet.py update
