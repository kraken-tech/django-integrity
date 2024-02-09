from django.db import models


class PrimaryKeyModel(models.Model):
    # Serialize must not be on because our tests try to create instances with clashing IDs.
    id = models.BigAutoField(primary_key=True, serialize=False)


class AlternativePrimaryKeyModel(models.Model):
    # Serialize must not be on because our tests try to create instances with clashing IDs.
    identity = models.BigAutoField(primary_key=True, serialize=False)


class ForeignKeyModel(models.Model):
    related = models.ForeignKey(PrimaryKeyModel, on_delete=models.CASCADE)


class ForeignKeyModel2(models.Model):
    related = models.ForeignKey(PrimaryKeyModel, on_delete=models.CASCADE)


class ForeignKeyModel3(models.Model):
    related_1 = models.ForeignKey(
        AlternativePrimaryKeyModel, on_delete=models.CASCADE, related_name="+"
    )
    related_2 = models.ForeignKey(
        AlternativePrimaryKeyModel,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
    )


class UniqueModel(models.Model):
    unique_field = models.IntegerField()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["unique_field"],
                name="unique_model_unique_field_key",
                deferrable=models.Deferrable.IMMEDIATE,
            ),
        )


class AlternativeUniqueModel(models.Model):
    unique_field = models.IntegerField(unique=True)
    unique_field_2 = models.IntegerField(unique=True)


class UniqueTogetherModel(models.Model):
    field_1 = models.IntegerField()
    field_2 = models.IntegerField()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["field_1", "field_2"],
                name="unique_together_model_field_1_field_2_key",
            ),
        )
