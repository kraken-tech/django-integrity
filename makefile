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
lint:
	pre-commit run --all-files

.PHONY:update
update:
	uv pip compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=dev \
		--output-file=requirements/development.txt
	uv pip compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=pytest-in-tox \
		--output-file=requirements/pytest-in-tox.txt \
		--unsafe-package django
	uv pip compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=release \
		--output-file=requirements/release.txt
	uv pip compile pyproject.toml \
		--quiet --upgrade --resolver=backtracking --strip-extras \
		--extra=tox \
		--output-file=requirements/tox.txt


# Implementation details
# ======================

# Pip install all required Python packages
.PHONY:install_python_packages
install_python_packages: install_prerequisites requirements/development.txt
	uv pip sync requirements/development.txt

.PHONY:install_prerequisites
install_prerequisites: requirements/prerequisites.txt
	pip install --quiet --requirement requirements/prerequisites.txt

.PHONY:install_pre_commit
install_pre_commit:
	pre-commit install

# Add new dependencies to requirements/development.txt whenever pyproject.toml changes
requirements/development.txt: pyproject.toml
	uv pip compile pyproject.toml \
		--quiet --resolver=backtracking --strip-extras \
		--extra=dev \
		--output-file=requirements/development.txt
