# Django Integrity

Django Integrity contains tools for controlling deferred constraints
and handling `IntegrityError`s in Django projects which use PostgreSQL.

## Deferrable constraints

Some PostgreSQL constraints can be defined as `DEFERRABLE`.
A constraint that is not deferred will be checked immediately after every command.
A deferred constraint check will be postponed until the end of the transaction.
A deferrable constraint will default to either `DEFERRED` or `IMMEDIATE`.

The utilities in `django_integrity.constraints` can
ensure a deferred constraint is checked immediately,
or defer an immediate constraint.

These alter the state of constraints until the end of the current transaction:

- `set_all_immediate(using=...)`
- `set_immedate(names=(...), using=...)`
- `set_deferred(names=(...), using=...)`

To enforce a constraint immediately within some limited part of a transaction,
use the `immediate(names=(...), using=...)` context manager.

### Why do we need this?

This is most likely to be useful when you want to catch a foreign-key violation
(i.e.: you have inserted a row which references different row which doesn't exist).

Django's foreign key constraints are deferred by default,
so they would normally raise an error only at the end of a transaction.
Using `try` to catch an `IntegrityError` from a foreign-key violation wouldn't work,
and you'd need to wrap the `COMMIT` instead, which is trickier.

By making the constraint `IMMEDIATE`,
the constraint would be checked on `INSERT`,
and it would be much easier to catch.

More generally,
if you have a custom deferrable constraint,
it may be useful to change the default behaviour with these tools.

## Refining `IntegrityError`

The `refine_integrity_error` context manager in `django_integrity.conversion`
will convert an `IntegrityError` into a more specific exception
based on a mapping of rules to your custom exceptions,
and will raise the `IntegrityError` if it doesn't match.

### Why do we need this?

When a database constraint is violated,
we usually expect to see an `IntegrityError`.

Sometimes we need more information about the error:
was it a unique constraint violation, or a check-constraint, or a not-null constraint?
Perhaps we ran out of 32-bit integers for our ID column?
Failing to be specific on these points could lead to bugs
where we catch an exception without realising it was not the one we expected.

### Example

```python
from django_integrity import conversion
from users.models import User


class UserAlreadyExists(Exception): ...
class EmailCannotBeNull(Exception): ...
class EmailMustBeLowerCase(Exception): ...


def create_user(email: str) -> User:
    """
    Creates a user with the provided email address.

    Raises:
        UserAlreadyExists: If the email was not unique.
        EmailCannotBeNull: If the email was None.
        EmailMustBeLowerCase: If the email had a non-lowercase character.
    """
    rules = {
        conversion.Unique(model=User, fields=("email",)): UserAlreadyExists,
        conversion.NotNull(model=User, field="email"): EmailCannotBeNull,
        conversion.Named(name="constraint_islowercase"): EmailMustBeLowerCase,
    }
    with conversion.refine_integrity_error(rules):
        User.objects.create(email=email)
```

## Supported dependencies

This package is tested against:

- Python 3.10, 3.11, or 3.12.
- Django 4.1, 4.2, or 5.0.
- PostgreSQL 12 to 16.
- psycopg2 and psycopg3.
