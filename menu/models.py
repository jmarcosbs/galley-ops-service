from common.models import (
    CommonTimedModel,
    CommonUUIDModel,
    CommonPriceModel,
    CommonAvailableModel,
)
from django.db import models
from nfce.models import NCM


class MenuBaseModel(CommonTimedModel, CommonUUIDModel):
    class Meta:
        abstract = True


class Category(MenuBaseModel):
    name = models.CharField("nome", max_length=255)
    color = models.CharField("cor", max_length=6)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name


class SideDish(MenuBaseModel, CommonAvailableModel):
    name = models.CharField("nome", max_length=255)

    class Meta:
        verbose_name = "Acompanhamento"
        verbose_name_plural = "Acompanhamentos"

    def __str__(self):
        return self.name


class SideDishOption(MenuBaseModel):
    side_dishes = models.ManyToManyField(
        SideDish, verbose_name="acompanhamentos", related_name="options"
    )
    default_side_dish = models.ForeignKey(
        SideDish,
        on_delete=models.CASCADE,
        verbose_name="acompanhamento padrão",
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
        if not self.pk:
            return "Nova opção de acompanhamento"

        dishes = list(self.side_dishes.order_by("name").values_list("name", flat=True))
        return (
            ", ".join(dishes) + f" - Padrão: ({self.default_side_dish.name})"
            if dishes
            else f"Opção {self.uuid}"
        )


class DepartmentChoices(models.TextChoices):
    KITCHEN = "kitchen", "Cozinha"
    BAR = "bar", "Copa"


class Dish(MenuBaseModel, CommonPriceModel, CommonAvailableModel):
    name = models.CharField("nome", max_length=255)
    description = models.TextField("descrição", blank=True, null=True)
    ncm = models.ForeignKey("nfce.NCM", verbose_name="NCM", on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, verbose_name="categoria", on_delete=models.CASCADE
    )
    department = models.CharField(
        "departamento", max_length=255, choices=DepartmentChoices.choices
    )
    show_on_public_menu = models.BooleanField(
        "mostrar no cardápio público",
        default=False,
        help_text="Controla se o item aparece na landing page pública.",
    )
    side_dish_options = models.ManyToManyField(
        SideDishOption,
        verbose_name="opções de acompanhamento",
        blank=True,
        related_name="dishes",
        help_text="Opções de acompanhamento disponíveis ao pedir este prato.",
    )

    class Meta:
        verbose_name = "Item do Cardápio"
        verbose_name_plural = "Itens do Cardápio"

    def __str__(self):
        return self.name


class CustomDish(MenuBaseModel, CommonPriceModel):
    name = models.CharField("nome", max_length=255)
    ncm = models.ForeignKey("nfce.NCM", verbose_name="NCM", on_delete=models.CASCADE)
    department = models.CharField(
        "departamento", max_length=255, choices=DepartmentChoices.choices
    )

    class Meta:
        verbose_name = "Item Customizado"
        verbose_name_plural = "Itens Customizados"

    def __str__(self):
        return self.name
