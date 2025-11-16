import re

from django.db import models


def normalize_code(value: str) -> str:
    """Strip punctuation and whitespace from NCM codes."""
    return re.sub(r"[\W_]+", "", value or "", flags=re.UNICODE)


class NCM(models.Model):
    code = models.CharField("código", max_length=20, unique=True)
    description = models.TextField("descrição")

    class Meta:
        verbose_name = "NCM"
        verbose_name_plural = "NCMs"
        ordering = ["code"]

    def save(self, *args, **kwargs):
        self.code = normalize_code(str(self.code))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"
