import django_integrity as package


def test_has_docstring() -> None:
    assert package.__doc__ is not None
