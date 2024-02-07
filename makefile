SHELL=/bin/bash

.PHONY:help
help:
	@echo "Available targets:"
	@echo "  help: Show this help message"
	@echo "  package: Build a wheel package"


# Standard entry points
# =====================

.PHONY:package
package:
	pip wheel .
