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
	uv lock --upgrade --resolver=backtracking


# Implementation details
# ======================

# Install all required Python packages
.PHONY:install_python_packages
install_python_packages:
	uv sync --group dev

.PHONY:install_pre_commit
install_pre_commit:
	pre-commit install

# Add new dependencies to uv.lock whenever pyproject.toml changes
uv.lock: pyproject.toml
	uv lock --upgrade --resolver=backtracking
