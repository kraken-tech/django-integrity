from django.db import models


class PrimaryKeyModel(models.Model):
    pass


class ForeignKeyModel(models.Model):
    related = models.ForeignKey(PrimaryKeyModel, on_delete=models.CASCADE)
