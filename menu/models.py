from common.models import (
    CommonTimedModel,
    CommonUUIDModel,
    CommonPriceModel,
    CommonAvailableModel,
)
from django.db import models


class MenuBaseModel(CommonTimedModel, CommonUUIDModel):
    class Meta:
        abstract = True


class Category(MenuBaseModel):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=6)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name


class SideDish(MenuBaseModel, CommonPriceModel, CommonAvailableModel):
    name = models.CharField(max_length=255)


class SideDishOption(MenuBaseModel, CommonPriceModel):
    side_dishes = models.ManyToManyField(SideDish, related_name="options")
    default_side_dish = models.ForeignKey(
        SideDish,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="default_for_side_dish_options",
    )

    constraints = [
        models.CheckConstraint(
            check=models.Q(side_dishes__count__lte=3),
            name="max_3_side_dishes_per_option",
        )
    ]

    class Meta:
        verbose_name = "Opção de Acompanhamento"
        verbose_name_plural = "Opções de Acompanhamento"

    def __str__(self):
        return self.name


class DepartmentChoices(models.TextChoices):
    KITCHEN = "kitchen", "Cozinha"
    BAR = "bar", "Copa"


class Dish(MenuBaseModel, CommonPriceModel, CommonAvailableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    ncm = models.BigIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    department = models.CharField(max_length=255, choices=DepartmentChoices.choices)
    side_dish_options = models.ManyToManyField(
        SideDishOption,
        blank=True,
        related_name="dishes",
        help_text="Opções de acompanhamento disponíveis ao pedir este prato.",
    )

    class Meta:
        verbose_name = "Item do Cardápio"
        verbose_name_plural = "Itens do Cardápio"

    def __str__(self):
        return self.name
