# Changelog

All notable changes to this project will be documented in this file.

## Unreleased changes

- Fix some incorrect type signatures.
  We were mistakenly asking for `django.db.models.Model` instead of `type[django_db.models.Model]` in:
    - `django_integrity.constraints.foreign_key_constraint_name`
    - `django_integrity.conversion.Unique`
    - `django_integrity.conversion.PrimaryKey`
    - `django_integrity.conversion.NotNull`
    - `django_integrity.conversion.ForeignKey`

## v0.1.0 - 2024-05-07

- Initial release! WOO!
- Tested against sensible combinations of:
    - Python 3.10, 3.11, and 3.12.
    - Django 4.1, 4.2, and 5.0.
    - PostgreSQL 12 to 16.
    - psycopg2 and psycopg3.
