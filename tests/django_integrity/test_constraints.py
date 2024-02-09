import pytest
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
