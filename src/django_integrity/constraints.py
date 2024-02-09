from django import db as django_db


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
