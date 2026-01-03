from decimal import Decimal

from rest_framework import serializers
from nfce.models import NCM
from orders.models import DishOrder, Ticket, TicketSettlement, TicketStatus

ACTIVE_TICKET_STATUSES = [TicketStatus.OPEN, TicketStatus.PARTIALLY_CLOSED]


def _get_active_ticket_or_error(number: int, is_outside: bool) -> Ticket:
    ticket = Ticket.objects.filter(
        number=number,
        is_outside=is_outside,
        status__in=ACTIVE_TICKET_STATUSES,
    ).first()
    if ticket is None:
        raise serializers.ValidationError("Este ticket não encontrado ou já fechado.")
    return ticket


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
            raise serializers.ValidationError(
                "Envie dish_uuid OU custom_dish, não ambos nem nenhum."
            )
        if custom and attrs.get("side_dishes"):
            raise serializers.ValidationError(
                "Itens customizados não aceitam acompanhamentos."
            )
        return attrs

    # TODO: Validar se acompanhamentos estão disponíveis para o prato


class OrderSerializer(serializers.Serializer):
    ticket = serializers.IntegerField()
    dishes = serializers.ListField(child=DishOrderSerializer())
    general_note = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    is_outside = serializers.BooleanField(required=False, default=False)


class TicketItemAddSerializer(DishOrderSerializer):
    ticket_number = serializers.IntegerField()
    is_outside = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        ticket_number = attrs["ticket_number"]
        is_outside = attrs.get("is_outside", False)
        ticket = _get_active_ticket_or_error(ticket_number, is_outside)
        self.context["ticket"] = ticket
        return attrs


class TicketItemRemoveSerializer(serializers.Serializer):
    ticket_number = serializers.IntegerField()
    is_outside = serializers.BooleanField(required=False, default=False)
    dish_order_uuid = serializers.UUIDField()
    quantity = serializers.FloatField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        ticket = _get_active_ticket_or_error(
            validated_data["ticket_number"], validated_data.get("is_outside", False)
        )
        self.context["ticket"] = ticket
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
    is_outside = serializers.BooleanField(required=False, default=False)
    dish_order_uuid = serializers.UUIDField()
    quantity = serializers.FloatField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("A quantidade deve ser maior que zero.")
        return value

    def validate(self, validated_data):
        validated_data = super().validate(validated_data)
        ticket = _get_active_ticket_or_error(
            validated_data["ticket_number"], validated_data.get("is_outside", False)
        )
        self.context["ticket"] = ticket
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
    is_outside = serializers.BooleanField(required=False, default=False)
    additions_percentage = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=Decimal("10")
    )
    discounts_percentage = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    items = serializers.ListField(child=TicketSettlementItemSerializer())

    def validate_additions_percentage(self, value: Decimal) -> Decimal:
        mandatory_percentage = Decimal("10")
        if value != mandatory_percentage:
            raise serializers.ValidationError("O acréscimo obrigatório é de 10%.")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        ticket = _get_active_ticket_or_error(
            attrs["ticket_number"], attrs.get("is_outside", False)
        )
        self.context["ticket"] = ticket
        return attrs


class TicketUpdateSerializer(serializers.Serializer):
    ticket_uuid = serializers.UUIDField()
    number = serializers.IntegerField(min_value=1)
    is_outside = serializers.BooleanField()

    def validate(self, attrs):
        ticket = Ticket.objects.filter(uuid=attrs["ticket_uuid"]).first()
        if ticket is None:
            raise serializers.ValidationError("Ticket não encontrado.")
        if ticket.status not in ACTIVE_TICKET_STATUSES:
            raise serializers.ValidationError(
                "Somente mesas abertas ou parcialmente fechadas podem ser atualizadas."
            )

        conflict_exists = Ticket.objects.filter(
            number=attrs["number"],
            is_outside=attrs["is_outside"],
            status__in=ACTIVE_TICKET_STATUSES,
        ).exclude(pk=ticket.pk)
        if conflict_exists.exists():
            raise serializers.ValidationError(
                "Já existe uma mesa aberta com este número e área."
            )

        attrs["ticket"] = ticket
        return attrs


class TicketSettlementCancelSerializer(serializers.Serializer):
    settlement_uuid = serializers.UUIDField()
    justification = serializers.CharField()

    def validate_settlement_uuid(self, value):
        settlement = (
            TicketSettlement.objects.select_related("ticket")
            .filter(uuid=value)
            .first()
        )
        if settlement is None:
            raise serializers.ValidationError("Fechamento não encontrado.")
        if settlement.canceled:
            raise serializers.ValidationError("Este fechamento já está cancelado.")

        required_fields = (
            "nfce_access_key",
            "nfce_authorization_protocol",
            "nfce_emitter_cnpj",
            "nfce_emitter_uf",
        )
        missing_fields = [field for field in required_fields if not getattr(settlement, field)]
        if missing_fields:
            raise serializers.ValidationError("Dados fiscais ausentes para cancelamento.")

        self.context["settlement"] = settlement
        return value

    def validate_justification(self, value):
        if len(value) < 15:
            raise serializers.ValidationError(
                "A justificativa deve ter pelo menos 15 caracteres."
            )
        return value
