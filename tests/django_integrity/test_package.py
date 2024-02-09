import pytest
from django import db

import django_integrity as package


def test_has_docstring() -> None:
    assert package.__doc__ is not None


@pytest.mark.django_db
def test_has_database() -> None:
    """Test that the database is available."""
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)
