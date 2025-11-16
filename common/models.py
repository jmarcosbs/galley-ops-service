import uuid
from typing import Any, cast
from django.db import models


class CommonTimedModel(models.Model):
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        abstract = True


class CommonUUIDModel(models.Model):
    uuid = models.UUIDField("UUID", default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class CommonPriceModel(models.Model):
    price = models.DecimalField(
        "preço", max_digits=10, decimal_places=2, default=0.00
    )

    class Meta:
        abstract = True


class CommonAvailableModel(models.Model):
    is_available = models.BooleanField("disponível", default=cast(Any, True))

    class Meta:
        abstract = True
