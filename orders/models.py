from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from common.models import CommonTimedModel, CommonUUIDModel
from menu.models import Dish, SideDish, SideDishOption


class Order(CommonTimedModel, CommonUUIDModel):
    ticket = models.ForeignKey(
        "orders.Ticket",
        on_delete=models.CASCADE,
        related_name="orders",
    )
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


class TicketStatus(models.TextChoices):
    OPEN = "open"
    CLOSED = "closed"
    PARTIALLY_CLOSED = "partially_paid"
    CANCELLED = "cancelled"


class Ticket(CommonUUIDModel, CommonTimedModel):
    number = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=TicketStatus.choices)

    def __str__(self):
        return f"Ticket #{self.number} ({self.status})"

    def refresh_status_from_orders(self):
        """
        Atualiza o status com base nos itens pendentes nos pedidos ligados ao ticket.
        - Se não houver itens pendentes, fecha.
        - Se houver liquidação e ainda restarem itens, marca como parcialmente fechado.
        """
        has_orders = self.orders.exists()
        has_pending_items = DishOrder.objects.filter(
            order__in=self.orders.all(), quantity__gt=0
        ).exists()

        if not has_orders or not has_pending_items:
            new_status = TicketStatus.CLOSED
        elif self.settlements.exists():
            new_status = TicketStatus.PARTIALLY_CLOSED
        else:
            new_status = TicketStatus.OPEN

        if self.status != new_status:
            self.status = new_status
            super().save(update_fields=["status", "updated_at"])

    # Adiciona constraint que um pedido só pode estar em um ticket
    # Adiciona constraint que um ticket só pode ter um pedido aberto
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["number"],
                condition=Q(status=TicketStatus.OPEN),
                name="unique_open_ticket_number",
            ),
        ]


class TicketSettlement(CommonUUIDModel, CommonTimedModel):
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="settlements"
    )
    settled_by = models.ForeignKey(User, on_delete=models.PROTECT)
    # Total antes dos acrescimos e descontos
    full_value = models.DecimalField(max_digits=10, decimal_places=2)
    additions_value = models.DecimalField(max_digits=10, decimal_places=2)
    discounts_value = models.DecimalField(max_digits=10, decimal_places=2)
    final_value = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Após salvar o settlement, garante que o ticket seja reavaliado
        self.ticket.refresh_status_from_orders()


class TicketSettlementItem(CommonUUIDModel, CommonTimedModel):
    settlement = models.ForeignKey(
        TicketSettlement, on_delete=models.CASCADE, related_name="items"
    )
    dish_order = models.ForeignKey(
        DishOrder, on_delete=models.PROTECT, related_name="settlement_items"
    )
    dish_order_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.FloatField()  # quanto deste item foi liquidado

    def save(self, *args, **kwargs):
        # Calcula delta para não descontar duas vezes em atualizações
        previous_quantity = (
            TicketSettlementItem.objects.get(pk=self.pk).quantity if self.pk else 0
        )
        delta = float(self.quantity) - float(previous_quantity)
        available = self.dish_order.quantity + previous_quantity
        if self.quantity > available:
            raise ValidationError(
                "Quantidade liquidada maior que o saldo do item do pedido."
            )

        result = super().save(*args, **kwargs)

        if delta:
            self.dish_order.quantity -= delta
            self.dish_order.save(update_fields=["quantity", "updated_at"])
            self.settlement.ticket.refresh_status_from_orders()

        return result
