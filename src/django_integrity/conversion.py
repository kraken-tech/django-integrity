from __future__ import annotations

import abc
import contextlib
import dataclasses
import re
from collections.abc import Iterator, Mapping

from django import db as django_db

try:
    import psycopg
except ImportError:
    import psycopg2 as psycopg


@contextlib.contextmanager
def refine_integrity_error(rules: Mapping[_Rule, Exception]) -> Iterator[None]:
    """
    Convert a generic IntegrityError into a more specific exception.

    The conversion is based on a mapping of rules to exceptions.

    Args:
        rules: A mapping of rules to the exceptions we'll raise if they match.

    Raises:
        An error from the rules mapping if an IntegrityError matches a rule.
        Otherwise, the original IntegrityError.
    """
    try:
        yield
    except django_db.IntegrityError as e:
        for rule, refined_error in rules.items():
            if rule.is_match(e):
                raise refined_error from e
        raise


class _Rule(abc.ABC):
    @abc.abstractmethod
    def is_match(self, error: django_db.IntegrityError) -> bool:
        """
        Determine if the rule matches the given IntegrityError.

        Args:
            error: The IntegrityError to check.

        Returns:
            True if the rule matches the error, False otherwise.
        """
        ...


@dataclasses.dataclass(frozen=True)
class Named(_Rule):
    """
    A constraint identified by its name.
    """

    name: str

    def is_match(self, error: django_db.IntegrityError) -> bool:
        if not isinstance(error.__cause__, psycopg.errors.IntegrityError):
            return False

        return error.__cause__.diag.constraint_name == self.name


@dataclasses.dataclass(frozen=True)
class Unique(_Rule):
    """
    A unique constraint defined by a model and a set of fields.
    """

    model: django_db.models.Model
    fields: tuple[str]

    _pattern = re.compile(r"Key \((?P<fields>.+)\)=\(.*\) already exists.")

    def is_match(self, error: django_db.IntegrityError) -> bool:
        if not isinstance(error.__cause__, psycopg.errors.UniqueViolation):
            return False

        match = self._pattern.match(error.__cause__.diag.message_detail)
        if match is None:
            return False

        return (
            tuple(match.group("fields").split(", ")) == self.fields
            and error.__cause__.diag.table_name == self.model._meta.db_table
        )


@dataclasses.dataclass(frozen=True)
class PrimaryKey(_Rule):
    """
    A unique constraint on the primary key of a model.

    If the model has no primary key, a PrimaryKeyDoesNotExist error is raised when
    trying to create a PrimaryKey rule.
    """

    model: django_db.models.Model

    _pattern = re.compile(r"Key \((?P<fields>.+)\)=\(.*\) already exists.")

    def __post_init__(self):
        """
        Ensure the model has a primary key.

        There's no sense in creating a rule to match a primary key constraint
        if the model has no primary key.

        This helps us to justify an assert statement in is_match.
        """
        if self.model._meta.pk is None:
            raise ModelHasNoPrimaryKey

    def is_match(self, error: django_db.IntegrityError) -> bool:
        if not isinstance(error.__cause__, psycopg.errors.UniqueViolation):
            return False

        match = self._pattern.match(error.__cause__.diag.message_detail)
        if match is None:
            return False

        # The assert below informs Mypy that self.model._meta.pk is not None.
        # This has been enforced in __post_init__,
        # so this should never raise an error in practice.
        assert self.model._meta.pk is not None

        return (
            tuple(match.group("fields").split(", ")) == (self.model._meta.pk.name,)
            and error.__cause__.diag.table_name == self.model._meta.db_table
        )


class ModelHasNoPrimaryKey(Exception):
    """
    Raised when trying to make a PrimaryKey rule for a model without a primary key.
    """


@dataclasses.dataclass(frozen=True)
class NotNull(_Rule):
    """
    A not-null constraint on a Model's field.
    """

    model: django_db.models.Model
    field: str

    def is_match(self, error: django_db.IntegrityError) -> bool:
        if not isinstance(error.__cause__, psycopg.errors.NotNullViolation):
            return False

        return (
            error.__cause__.diag.column_name == self.field
            and error.__cause__.diag.table_name == self.model._meta.db_table
        )


@dataclasses.dataclass(frozen=True)
class ForeignKey(_Rule):
    """
    A foreign key constraint on a Model's field.
    """

    model: django_db.models.Model
    field: str

    _detail_pattern = re.compile(
        r"Key \((?P<field>.+)\)=\((?P<value>.+)\) is not present in table"
    )

    def is_match(self, error: django_db.IntegrityError) -> bool:
        if not isinstance(error.__cause__, psycopg.errors.ForeignKeyViolation):
            return False

        detail_match = self._detail_pattern.match(error.__cause__.diag.message_detail)
        if detail_match is None:
            return False

        return (
            detail_match.group("field") == self.field
            and error.__cause__.diag.table_name == self.model._meta.db_table
        )
