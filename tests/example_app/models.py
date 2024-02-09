from django.db import models


class PrimaryKeyModel(models.Model):
    pass


class ForeignKeyModel(models.Model):
    related = models.ForeignKey(PrimaryKeyModel, on_delete=models.CASCADE)


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
