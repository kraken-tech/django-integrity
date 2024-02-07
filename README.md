# Django Integrity

Django Integrity contains tools for controlling deferred constraints
and handling IntegrityErrors in Django projects which use PostgreSQL.

## Supported dependencies

- Python 3.10, 3.11, or 3.12.

### Managing dependencies

Package dependencies are declared in `pyproject.toml`.

- _package_ dependencies in the `dependencies` array in the `[project]` section.
- _development_ dependencies in the `dev` array in the `[project.optional-dependencies]` section.
