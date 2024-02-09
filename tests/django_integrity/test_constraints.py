import pytest
from django import db as django_db
from django.core import exceptions

from django_integrity import constraints
from tests.example_app import models as test_models


class TestForeignKeyConstraintName:
    @pytest.mark.django_db
    def test_generated_name(self) -> None:
        # The ForeignKey constraint name is generated from the model and field.
        constraint_name = constraints.foreign_key_constraint_name(
            model=test_models.ForeignKeyModel,
            field_name="related",
            using="default",
        )

        assert (
            constraint_name == "example_app_foreignk_related_id_7403e50b_fk_example_a"
        )

    def test_not_a_foreign_key(self) -> None:
        # The field is not a ForeignKey.
        with pytest.raises(constraints.NotAForeignKey):
            constraints.foreign_key_constraint_name(
                model=test_models.PrimaryKeyModel,
                field_name="id",
                using="default",
            )

    def test_wrong_field_name(self) -> None:
        # The field name doesn't exist on the model.
        with pytest.raises(exceptions.FieldDoesNotExist):
            constraints.foreign_key_constraint_name(
                model=test_models.ForeignKeyModel,
                field_name="does_not_exist",
                using="default",
            )


class TestSetAllImmediate:
    @pytest.mark.django_db
    def test_all_constraints_set(self):
        constraints.set_all_immediate(using="default")

        with pytest.raises(django_db.IntegrityError):
            # The ForeignKey constraint should be enforced immediately.
            test_models.ForeignKeyModel.objects.create(related_id=42)

    @pytest.mark.django_db(transaction=True)
    def test_not_in_transaction(self):
        # Fail if we're not in a transaction.
        with pytest.raises(constraints.NotInTransaction):
            constraints.set_all_immediate(using="default")


class TestSetImmediate:
    @pytest.mark.django_db
    def test_set(self):
        constraint_name = constraints.foreign_key_constraint_name(
            model=test_models.ForeignKeyModel,
            field_name="related_id",
            using="default",
        )

        constraints.set_immediate(names=(constraint_name,), using="default")

        # An error should be raised immediately.
        with pytest.raises(django_db.IntegrityError):
            test_models.ForeignKeyModel.objects.create(related_id=42)

    @pytest.mark.django_db
    def test_not_set(self):
        # No constraint name is passed, so no constraints should be set to immediate.
        constraints.set_immediate(names=(), using="default")

        # No error should be raised.
        test_models.ForeignKeyModel.objects.create(related_id=42)

        # We catch the error here to prevent the test from failing in shutdown.
        with pytest.raises(django_db.IntegrityError):
            constraints.set_all_immediate(using="default")

    @pytest.mark.django_db(transaction=True)
    def test_not_in_transaction(self):
        # Fail if we're not in a transaction.
        with pytest.raises(constraints.NotInTransaction):
            constraints.set_immediate(names=(), using="default")


class TestSetDeferred:
    @pytest.mark.django_db
    def test_not_set(self):
        test_models.UniqueModel.objects.create(unique_field=42)

        # We pass no names, so no constraints should be set to deferred.
        constraints.set_deferred(names=(), using="default")

        # This constraint defaults to IMMEDIATE,
        # so an error should be raised immediately.
        with pytest.raises(django_db.IntegrityError):
            test_models.UniqueModel.objects.create(unique_field=42)

    @pytest.mark.django_db
    def test_set(self):
        test_models.UniqueModel.objects.create(unique_field=42)

        # We defer the constraint...
        constraint_name = "unique_model_unique_field_key"
        constraints.set_deferred(names=(constraint_name,), using="default")

        # ... so no error should be raised.
        test_models.UniqueModel.objects.create(unique_field=42)

        # We catch the error here to prevent the test from failing in shutdown.
        with pytest.raises(django_db.IntegrityError):
            constraints.set_all_immediate(using="default")

    @pytest.mark.django_db(transaction=True)
    def test_not_in_transaction(self):
        # Fail if we're not in a transaction.
        with pytest.raises(constraints.NotInTransaction):
            constraints.set_deferred(names=(), using="default")


class TestImmediate:
    @pytest.mark.django_db
    def test_constraint_not_enforced(self):
        """Constraints are not changed when not explicitly enforced."""
        # Call the context manager without any constraint names.
        with constraints.immediate((), using="default"):
            # Create an instance that violates a deferred constraint.
            # No error should be raised.
            test_models.ForeignKeyModel.objects.create(related_id=42)

        # We catch the error here to prevent the test from failing in shutdown.
        with pytest.raises(django_db.IntegrityError):
            constraints.set_all_immediate(using="default")

    @pytest.mark.django_db
    def test_constraint_enforced(self):
        """Constraints are enforced when explicitly enforced."""
        constraint_name = constraints.foreign_key_constraint_name(
            model=test_models.ForeignKeyModel,
            field_name="related_id",
            using="default",
        )

        # An error should be raised immediately.
        with pytest.raises(django_db.IntegrityError):
            with constraints.immediate((constraint_name,), using="default"):
                # Create an instance that violates a deferred constraint.
                test_models.ForeignKeyModel.objects.create(related_id=42)

    @pytest.mark.django_db
    def test_deferral_restored(self):
        """Constraints are restored to DEFERRED after the context manager."""
        constraint_name = constraints.foreign_key_constraint_name(
            model=test_models.ForeignKeyModel,
            field_name="related_id",
            using="default",
        )

        with constraints.immediate((constraint_name,), using="default"):
            pass

        # Create an instance that violates a deferred constraint.
        # No error should be raised, because the constraint should be deferred again.
        test_models.ForeignKeyModel.objects.create(related_id=42)

        # We catch the error here to prevent the test from failing in shutdown.
        with pytest.raises(django_db.IntegrityError):
            constraints.set_all_immediate(using="default")

    @pytest.mark.django_db(transaction=True)
    def test_not_in_transaction(self):
        # Fail if we're not in a transaction.
        with pytest.raises(constraints.NotInTransaction):
            with constraints.immediate((), using="default"):
                pass
