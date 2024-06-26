# Changelog

All notable changes to this project will be documented in this file.

## Unreleased changes

## v0.2.0 - 2024-05-13

### Changed

- Change type signature of `django_integrity.conversion.refine_integrity_error`.
  Instead of accepting `Mapping[_Rule, Exception]`, it now accepts `Sequence[tuple[_Rule, Exception | type[Exception]]`.
  This prevents issues with typing, and removes the need for `_Rule` to be hashable.
- Install CI and development requirements with `uv` instead of `pip-tools`.

### Fixed

- Fix some more incorrect type signatures:
    - `django_integrity.conversion.Unique.fields` was erroneously `tuple[str]` instead of `tuple[str, ...]`.
- Protect against previously-unhandled potential `None` in errors from Psycopg.

## v0.1.1 - 2024-05-09

- Fix some incorrect type signatures.
  We were mistakenly asking for `django.db.models.Model` instead of `type[django.db.models.Model]` in:
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
