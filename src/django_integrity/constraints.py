import contextlib
from collections.abc import Iterator, Sequence

from django import db as django_db

try:
    from psycopg import sql
except ImportError:
    from psycopg2 import sql


# Note [Deferrable constraints]
# -----------------------------
# Only some types of PostgreSQL constraint can be DEFERRED, and
# they may be deferred if they are created with the DEFERRABLE option.
#
# These types of constraints can be DEFERRABLE:
# - UNIQUE
# - PRIMARY KEY
# - REFERENCES (foreign key)
# - EXCLUDE
#
# These types of constraints can never be DEFERRABLE:
# - CHECK
# - NOT NULL
#
# By default, Django makes foreign key constraints DEFERRABLE INITIALLY DEFERRED,
# so they are checked at the end of the transaction,
# rather than when the statement is executed.
#
# All other constraints are IMMEDIATE (and not DEFERRABLE) by default.
# This can be changed by passing the `deferrable` argument to the constraint.
#
# Further reading:
# - https://www.postgresql.org/docs/current/sql-set-constraints.html
# - https://www.postgresql.org/docs/current/sql-createtable.html
# - https://docs.djangoproject.com/en/5.0/ref/models/constraints/#deferrable


@contextlib.contextmanager
def immediate(names: Sequence[str], *, using: str) -> Iterator[None]:
    """
    Temporarily set named DEFERRABLE constraints to IMMEDIATE.

    This is useful for catching constraint violations as soon as they occur,
    rather than at the end of the transaction.

    This is especially useful for foreign key constraints in Django,
    which are DEFERRED by default.

    We presume that any provided constraints were previously DEFERRED,
    and we restore them to that state after the context manager exits.

    To be sure that the constraints are restored to DEFERRED
    even if an exception is raised, we use a savepoint.

    This could be expensive if used in a loop because on every iteration we would
    create and close (or roll back) a savepoint, and set and unset the constraint state.

    # See Note [Deferrable constraints]

    Args:
        names: The names of the constraints to change.
        using: The name of the database connection to use.

    Raises:
        NotInTransaction: When we try to change constraints outside of a transaction.
    """
    set_immediate(names, using=using)
    try:
        with django_db.transaction.atomic(using=using):
            yield
    finally:
        set_deferred(names, using=using)


def set_all_immediate(*, using: str) -> None:
    """
    Set all constraints to IMMEDIATE for the remainder of the transaction.

    # See Note [Deferrable constraints]

    Args:
        using: The name of the database connection to use.

    Raises:
        NotInTransaction: When we try to change constraints outside of a transaction.
    """
    if django_db.transaction.get_autocommit(using):
        raise NotInTransaction

    with django_db.connections[using].cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")


def set_immediate(names: Sequence[str], *, using: str) -> None:
    """
    Set particular constraints to IMMEDIATE for the remainder of the transaction.

    # See Note [Deferrable constraints]

    Args:
        names: The names of the constraints to set to IMMEDIATE.
        using: The name of the database connection to use.

    Raises:
        NotInTransaction: When we try to change constraints outside of a transaction.
    """
    if django_db.transaction.get_autocommit(using):
        raise NotInTransaction

    if not names:
        return

    query = sql.SQL("SET CONSTRAINTS {names} IMMEDIATE").format(
        names=sql.SQL(", ").join(sql.Identifier(name) for name in names)
    )

    with django_db.connections[using].cursor() as cursor:
        cursor.execute(query)


def set_deferred(names: Sequence[str], *, using: str) -> None:
    """
    Set particular constraints to DEFERRED for the remainder of the transaction.

    # See Note [Deferrable constraints]

    Args:
        names: The names of the constraints to set to DEFERRED.
        using: The name of the database connection to use.

    Raises:
        NotInTransaction: When we try to change constraints outside of a transaction.
    """
    if django_db.transaction.get_autocommit(using):
        raise NotInTransaction

    if not names:
        return

    query = sql.SQL("SET CONSTRAINTS {names} DEFERRED").format(
        names=sql.SQL(", ").join(sql.Identifier(name) for name in names)
    )

    with django_db.connections[using].cursor() as cursor:
        cursor.execute(query)


class NotInTransaction(Exception):
    """
    Raised when we try to change the state of constraints outside of a transaction.

    It doesn't make sense to change the state of constraints outside of a transaction,
    because the change of state would only last for the remainder of the transaction.

    See https://www.postgresql.org/docs/current/sql-set-constraints.html
    """


def foreign_key_constraint_name(
    model: django_db.models.Model, field_name: str, *, using: str
) -> str:
    """
    Calculate FK constraint name for a model's field.

    Django's constraint names are based on the names of the tables and columns involved.

    Because there is a 63-character limit on constraint names in PostgreSQL,
    Django uses a hash to shorten the names of long columns.
    This means that the constraint name is not deterministic based on the model and field alone.

    Django surely ought to have a public method for this, but it doesn't!

    Args:
        model: The model that contains the field.
        field_name: The name of the field.
        using: The name of the database connection to use.

    Raises:
        django.core.exceptions.FieldDoesNotExist: When the field is not on the model.
        NotAForeignKey: When the field is not a foreign key.

    Returns:
        The name of the foreign key constraint.
    """
    field = model._meta.get_field(field_name)

    remote_field = field.remote_field
    if remote_field is None:
        raise NotAForeignKey

    to_table = remote_field.model._meta.db_table
    to_field = remote_field.name
    suffix = f"_fk_{to_table}_{to_field}"

    connection = django_db.connections[using]
    with connection.schema_editor() as editor:
        # The _fk_constraint_name method is not part of the public API,
        # and only exists on the PostgreSQL schema editor.
        # Django-stubs does not know about this method, so we have to use a type ignore.
        constraint_name = editor._fk_constraint_name(model, field, suffix)  # type: ignore[attr-defined]

    return str(constraint_name).removeprefix('"').removesuffix('"')


class NotAForeignKey(Exception):
    """
    Raised when we ask for the FK constraint name of a field that is not a foreign key.
    """
