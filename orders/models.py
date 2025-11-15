from django.contrib.auth.models import User
from django.db import models

from common.models import CommonTimedModel, CommonUUIDModel
from menu.models import Dish, SideDish, SideDishOption


class Order(CommonTimedModel, CommonUUIDModel):
    ticket = models.IntegerField()
    waiter = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    dishes = models.ManyToManyField(
        Dish,
        through="DishOrder",
        related_name="orders",
        blank=True,
    )


class DishOrder(CommonTimedModel, CommonUUIDModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="dish_orders",
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name="dish_orders",
    )
    quantity = models.FloatField()
    note = models.TextField(blank=True, null=True)


class DishOrderSideDish(CommonUUIDModel, CommonTimedModel):
    dish_order = models.ForeignKey(
        DishOrder, on_delete=models.CASCADE, related_name="side_dish_selections"
    )
    option = models.ForeignKey(SideDishOption, on_delete=models.PROTECT)
    side_dish = models.ForeignKey(SideDish, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("dish_order", "side_dish")
