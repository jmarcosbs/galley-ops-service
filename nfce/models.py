import re

from django.db import models


def normalize_code(value: str) -> str:
    """Strip punctuation and whitespace from NCM codes."""
    return re.sub(r"[\W_]+", "", value or "", flags=re.UNICODE)


class NCM(models.Model):
    code = models.CharField("código", max_length=20, unique=True)
    description = models.TextField("descrição")
    national_tax = models.DecimalField(
        "imposto nacional", max_digits=10, decimal_places=2
    )
    import_tax = models.DecimalField(
        "imposto importação", max_digits=10, decimal_places=2
    )
    state_tax = models.DecimalField(
        "imposto estadual", max_digits=10, decimal_places=2
    )
    municipal_tax = models.DecimalField(
        "imposto municipal", max_digits=10, decimal_places=2
    )
    vigency_start = models.DateField("data de início de vigência")
    vigency_end = models.DateField("data de fim de vigência")

    class Meta:
        verbose_name = "NCM"
        verbose_name_plural = "NCMs"
        ordering = ["code"]

    def save(self, *args, **kwargs):
        self.code = normalize_code(str(self.code))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"
