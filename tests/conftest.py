import os

import pytest
from pytest_django import fixtures, lazy_django


@pytest.fixture(scope="session")
def django_db_modify_db_settings_tox_suffix() -> None:
    """
    Suffixed test databases names for tox workers to avoid clashing databases.

    This works around a bug in pytest-django, where the wrong environment
    variable is used.

    Ref: https://github.com/pytest-dev/pytest-django/pull/1112
    """
    lazy_django.skip_if_no_django()

    tox_environment = os.getenv("TOX_ENV_NAME")
    if tox_environment:
        fixtures._set_suffix_to_test_databases(suffix=tox_environment)
