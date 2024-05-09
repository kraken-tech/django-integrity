import pytest
from django import db as django_db

from django_integrity import constraints, conversion
from tests.example_app import models as test_models


class SimpleError(Exception):
    pass


class TestRefineIntegrityError:
    def test_no_rules(self) -> None:
        # It is legal to call the context manager without any rules.
        with conversion.refine_integrity_error(rules=()):
            pass


@pytest.mark.django_db
class TestNamedConstraint:
    def test_error_refined(self) -> None:
        # Create a unique instance so that we can violate the constraint later.
        test_models.UniqueModel.objects.create(unique_field=42)

        rules = ((conversion.Named(name="unique_model_unique_field_key"), SimpleError),)

        # The original error should be transformed into our expected error.
        with pytest.raises(SimpleError):
            with conversion.refine_integrity_error(rules):
                test_models.UniqueModel.objects.create(unique_field=42)

    def test_rules_mismatch(self) -> None:
        # Create a unique instance so that we can violate the constraint later.
        test_models.UniqueModel.objects.create(unique_field=42)

        # No constraints match the error:
        rules = ((conversion.Named(name="nonexistent_constraint"), SimpleError),)

        # The original error should be raised.
        with pytest.raises(django_db.IntegrityError):
            with conversion.refine_integrity_error(rules):
                test_models.UniqueModel.objects.create(unique_field=42)


@pytest.mark.django_db
class TestUnique:
    def test_error_refined(self) -> None:
        # Create a unique instance so that we can violate the constraint later.
        test_models.UniqueModel.objects.create(unique_field=42)

        rules = (
            (
                conversion.Unique(
                    model=test_models.UniqueModel, fields=("unique_field",)
                ),
                SimpleError,
            ),
        )

        # The original error should be transformed into our expected error.
        with pytest.raises(SimpleError):
            with conversion.refine_integrity_error(rules):
                test_models.UniqueModel.objects.create(unique_field=42)

    def test_multiple_fields(self) -> None:
        # Create a unique instance so that we can violate the constraint later.
        test_models.UniqueTogetherModel.objects.create(field_1=1, field_2=2)

        rules = (
            (
                conversion.Unique(
                    model=test_models.UniqueTogetherModel, fields=("field_1", "field_2")
                ),
                SimpleError,
            ),
        )

        # The original error should be transformed into our expected error.
        with pytest.raises(SimpleError):
            with conversion.refine_integrity_error(rules):
                test_models.UniqueTogetherModel.objects.create(field_1=1, field_2=2)

    @pytest.mark.parametrize(
        "Model, field",
        (
            # Wrong model, despite matching field name.
            (
                test_models.AlternativeUniqueModel,
                "unique_field",
            ),
            # Wrong field, despite matching model.
            (
                test_models.UniqueModel,
                "id",
            ),
        ),
        ids=("wrong_model", "wrong_field"),
    )
    def test_rules_mismatch(
        self,
        Model: type[test_models.AlternativeUniqueModel | test_models.UniqueModel],
        field: str,
    ) -> None:
        # A rule that matches a similar looking, but different, unique constraint.
        # Create a unique instance so that we can violate the constraint later.
        test_models.UniqueModel.objects.create(unique_field=42)

        rules = ((conversion.Unique(model=Model, fields=(field,)), SimpleError),)

        # We shouldn't transform the error, because it didn't match the rule.
        with pytest.raises(django_db.IntegrityError):
            with conversion.refine_integrity_error(rules):
                test_models.UniqueModel.objects.create(unique_field=42)


@pytest.mark.django_db
class TestPrimaryKey:
    @pytest.mark.parametrize(
        "ModelClass",
        (
            test_models.PrimaryKeyModel,
            test_models.AlternativePrimaryKeyModel,
        ),
    )
    def test_error_refined(
        self,
        ModelClass: type[test_models.PrimaryKeyModel]
        | type[test_models.AlternativePrimaryKeyModel],
    ) -> None:
        """
        The primary key of a model is extracted from the model.

        This test internally refers to the models primary key using "pk".
        "pk" is Django magic that refers to the primary key of the model.
        On PrimaryKeyModel, the primary key is "id".
        On AlternativePrimaryKeyModel, the primary key is "identity".
        """
        # Create a unique instance so that we can violate the constraint later.
        existing_primary_key = ModelClass.objects.create().pk

        rules = ((conversion.PrimaryKey(model=ModelClass), SimpleError),)

        # The original error should be transformed into our expected error.
        with pytest.raises(SimpleError):
            with conversion.refine_integrity_error(rules):
                ModelClass.objects.create(pk=existing_primary_key)

    def test_rules_mismatch(self) -> None:
        # Create a unique instance so that we can violate the constraint later.
        existing_primary_key = test_models.PrimaryKeyModel.objects.create().pk

        # A similar rule, but for a different model with the same field name..
        rules = ((conversion.PrimaryKey(model=test_models.UniqueModel), SimpleError),)

        # The original error should be raised.
        with pytest.raises(django_db.IntegrityError):
            with conversion.refine_integrity_error(rules):
                test_models.PrimaryKeyModel.objects.create(pk=existing_primary_key)

    def test_model_without_primary_key(self) -> None:
        """
        We cannot create a PrimaryKey rule for a model without a primary key.
        """
        with pytest.raises(conversion.ModelHasNoPrimaryKey):
            conversion.PrimaryKey(
                # An abstract model without a primary key.
                model=test_models.AbstractModel
            )


@pytest.mark.django_db
class TestNotNull:
    def test_error_refined(self) -> None:
        rules = (
            (
                conversion.NotNull(model=test_models.UniqueModel, field="unique_field"),
                SimpleError,
            ),
        )

        # The original error should be transformed into our expected error.
        with pytest.raises(SimpleError):
            with conversion.refine_integrity_error(rules):
                # We ignore the type error because it's picking up on the error we're testing.
                test_models.UniqueModel.objects.create(unique_field=None)  # type: ignore[misc]

    def test_model_mismatch(self) -> None:
        # Same field, but different model.
        rules = (
            (
                conversion.NotNull(
                    model=test_models.AlternativeUniqueModel, field="unique_field"
                ),
                SimpleError,
            ),
        )

        with pytest.raises(django_db.IntegrityError):
            with conversion.refine_integrity_error(rules):
                # We ignore the type error because it's picking up on the error we're testing.
                test_models.UniqueModel.objects.create(unique_field=None)  # type: ignore[misc]

    def test_field_mismatch(self) -> None:
        # Same model, but different field.
        rules = (
            (
                conversion.NotNull(
                    model=test_models.AlternativeUniqueModel, field="unique_field_2"
                ),
                SimpleError,
            ),
        )

        # The original error should be raised.
        with pytest.raises(django_db.IntegrityError):
            with conversion.refine_integrity_error(rules):
                test_models.AlternativeUniqueModel.objects.create(
                    # We ignore the type error because it's picking up on the error we're testing.
                    unique_field=None,  # type: ignore[misc]
                    unique_field_2=42,
                )


@pytest.mark.django_db
class TestForeignKey:
    def test_error_refined(self) -> None:
        rules = (
            (
                conversion.ForeignKey(
                    model=test_models.ForeignKeyModel, field="related_id"
                ),
                SimpleError,
            ),
        )
        constraints.set_all_immediate(using="default")

        # The original error should be transformed into our expected error.
        with pytest.raises(SimpleError):
            with conversion.refine_integrity_error(rules):
                # Create a ForeignKeyModel with a related_id that doesn't exist.
                test_models.ForeignKeyModel.objects.create(related_id=42)

    def test_source_mismatch(self) -> None:
        # The field name matches, but the source model is different.
        rules = (
            (
                conversion.ForeignKey(
                    model=test_models.ForeignKeyModel2, field="related_id"
                ),
                SimpleError,
            ),
        )
        constraints.set_all_immediate(using="default")

        with pytest.raises(django_db.IntegrityError):
            with conversion.refine_integrity_error(rules):
                test_models.ForeignKeyModel.objects.create(related_id=42)

    def test_field_mismatch(self) -> None:
        # The source model matches, but the field name is different.
        rules = (
            (
                conversion.ForeignKey(
                    model=test_models.ForeignKeyModel3, field="related_2_id"
                ),
                SimpleError,
            ),
        )
        constraints.set_all_immediate(using="default")

        with pytest.raises(django_db.IntegrityError):
            with conversion.refine_integrity_error(rules):
                test_models.ForeignKeyModel3.objects.create(related_1_id=42)
