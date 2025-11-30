from rest_framework import serializers

from orders.models import DishOrder, Ticket, TicketStatus


class SideDishSerializer(serializers.Serializer):
    side_dish_uuid = serializers.UUIDField()


class DishOrderSerializer(serializers.Serializer):
    dish_uuid = serializers.UUIDField()
    amount = serializers.FloatField()
    dish_note = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    side_dishes = serializers.ListField(
        child=SideDishSerializer(), required=False, allow_empty=True
    )

    # TODO: Validar se acompanhamentos estão disponíveis para o prato


class OrderSerializer(serializers.Serializer):
    ticket = serializers.IntegerField()
    dishes = serializers.ListField(child=DishOrderSerializer())
    general_note = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )


class TicketSettlementItemSerializer(serializers.Serializer):
    dish_order_uuid = serializers.UUIDField()
    dish_order_quantity = serializers.FloatField()

    # Verifica se o dish_order_uuid pertence a um dish_order do ticket
    def validate_dish_order_uuid(self, value):
        dish_order = DishOrder.objects.get(uuid=value)
        ticket = self.context.get("ticket")
        if ticket is not None and dish_order.order.ticket != ticket:
            raise serializers.ValidationError("Este item não pertence a este ticket.")
        return value

    def validate(self, validated_data):
        dish_order = DishOrder.objects.get(uuid=validated_data["dish_order_uuid"])
        if validated_data["dish_order_quantity"] > dish_order.quantity:
            raise serializers.ValidationError(
                "A quantidade informada é maior que o saldo do item do pedido."
            )

        return validated_data


class TicketSettlementSerializer(serializers.Serializer):
    ticket_number = serializers.IntegerField()
    additions_percentage = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    discounts_percentage = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    items = serializers.ListField(child=TicketSettlementItemSerializer())

    def validate_ticket_number(self, value):
        ticket = Ticket.objects.filter(
            number=value, status__in=[TicketStatus.OPEN, TicketStatus.PARTIALLY_CLOSED]
        ).first()
        if ticket is None:
            raise serializers.ValidationError(
                "Este ticket não encontrado ou já fechado."
            )

        self.context["ticket"] = ticket
        return value
