from rest_framework import serializers
from nfce.models import NCM
from orders.models import DishOrder, Ticket, TicketStatus


class SideDishSerializer(serializers.Serializer):
    side_dish_uuid = serializers.UUIDField()

class CustomDishSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    ncm = serializers.IntegerField()
    department = serializers.CharField()
    
    def validate_ncm(self, value):
        ncm = NCM.objects.get(code=value)
        if ncm is None:
            raise serializers.ValidationError("NCM não encontrado.")
        return value

class DishOrderSerializer(serializers.Serializer):
    # Recebe um prato
    dish_uuid = serializers.UUIDField(required=False, allow_null=True)
    
    # Ou um item customizado
    custom_dish = CustomDishSerializer(required=False, allow_null=True)
    
    amount = serializers.FloatField()
    dish_note = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    side_dishes = serializers.ListField(
        child=SideDishSerializer(), required=False, allow_empty=True
    )
    
    def validate(self, attrs):
        dish_uuid = attrs.get("dish_uuid")
        custom = attrs.get("custom_dish")
        if bool(dish_uuid) == bool(custom):
            raise serializers.ValidationError("Envie dish_uuid OU custom_dish, não ambos nem nenhum.")
        if custom and attrs.get("side_dishes"):
            raise serializers.ValidationError("Itens customizados não aceitam acompanhamentos.")
        return attrs

    # TODO: Validar se acompanhamentos estão disponíveis para o prato


class OrderSerializer(serializers.Serializer):
    ticket = serializers.IntegerField()
    dishes = serializers.ListField(child=DishOrderSerializer())
    general_note = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )


class TicketItemAddSerializer(DishOrderSerializer):
    ticket_number = serializers.IntegerField()

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


class TicketItemRemoveSerializer(serializers.Serializer):
    ticket_number = serializers.IntegerField()
    dish_order_uuid = serializers.UUIDField()
    quantity = serializers.FloatField()

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

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    def validate(self, validated_data):
        ticket = self.context.get("ticket")
        dish_order = (
            DishOrder.objects.select_related("order__ticket")
            .filter(uuid=validated_data["dish_order_uuid"], order__ticket=ticket)
            .first()
        )
        if dish_order is None:
            raise serializers.ValidationError(
                "Este item não pertence ao ticket informado."
            )

        if validated_data["quantity"] > dish_order.quantity:
            raise serializers.ValidationError(
                "A quantidade informada é maior que o saldo do item."
            )

        self.context["dish_order"] = dish_order
        return validated_data


class TicketItemIncreaseSerializer(serializers.Serializer):
    ticket_number = serializers.IntegerField()
    dish_order_uuid = serializers.UUIDField()
    quantity = serializers.FloatField()

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

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    def validate(self, validated_data):
        ticket = self.context.get("ticket")
        dish_order = (
            DishOrder.objects.select_related("order__ticket")
            .filter(uuid=validated_data["dish_order_uuid"], order__ticket=ticket)
            .first()
        )
        if dish_order is None:
            raise serializers.ValidationError(
                "Este item não pertence ao ticket informado."
            )

        self.context["dish_order"] = dish_order
        return validated_data


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
