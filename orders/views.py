from contextlib import AbstractContextManager
from decimal import Decimal
from typing import cast

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.models import Dish, SideDish
from orders.helpers import OrderHelper
from orders.selectors import serialize_open_tables
from orders.serializers import (
    OrderSerializer,
    TicketSettlementSerializer,
)
from orders.models import (
    DishOrder,
    DishOrderSideDish,
    Order,
    Ticket,
    TicketSettlement,
    TicketSettlementItem,
    TicketStatus,
)
from orders.services import broadcast_open_tables
from orders.types import (
    SerializedOrderDataType,
    SerializedSettlementDataType,
    SerializedSettlementItemDataType,
)
from printer.service import PrintService
from telegram.service import TelegramService
import logging

logger = logging.getLogger(__name__)


class OrderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        user = request.user

        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "Order payload inválido: %s | data=%s", serializer.errors, request.data
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serialized_order_data: SerializedOrderDataType = cast(
            SerializedOrderDataType, serializer.validated_data
        )

        ticket_number = serialized_order_data["ticket"]

        try:
            with cast(AbstractContextManager, transaction.atomic()):
                ticket = Ticket.objects.filter(
                    number=ticket_number,
                    status__in=[TicketStatus.OPEN, TicketStatus.PARTIALLY_CLOSED],
                ).first()

                if not ticket:
                    ticket = Ticket.objects.create(
                        number=ticket_number, created_by=user, status=TicketStatus.OPEN
                    )
                elif ticket.status == TicketStatus.CLOSED:
                    raise ValidationError("Este ticket já está fechado.")

                order = Order.objects.create(
                    ticket=ticket,
                    waiter=user,
                    note=serialized_order_data.get("general_note"),
                )

                for dish_data in serialized_order_data["dishes"]:
                    dish = Dish.objects.get(uuid=dish_data["dish_uuid"])
                    dish_order = DishOrder.objects.create(
                        order=order,
                        dish=dish,
                        quantity=dish_data["amount"],
                        note=dish_data.get("dish_note"),
                    )

                    for side_dish_data in dish_data.get("side_dishes", []):
                        side_dish = SideDish.objects.get(
                            uuid=side_dish_data["side_dish_uuid"]
                        )
                        option = dish.side_dish_options.filter(
                            side_dishes=side_dish
                        ).first()
                        if not option:
                            raise ValidationError(
                                f"Acompanhamento {side_dish} não disponível para {dish}."
                            )
                        DishOrderSideDish.objects.create(
                            dish_order=dish_order, option=option, side_dish=side_dish
                        )

            # Envia pedido para impressão
            print_service = PrintService()
            printed, _, response_text = print_service.print_order(order)
            if not printed:
                raise Exception(f"Erro ao imprimir pedido: {response_text}")

        except ValidationError as exc:
            return Response(
                {"detail": exc.detail if hasattr(exc, "detail") else str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Dish.DoesNotExist:
            return Response(
                {"detail": "Prato não encontrado."}, status=status.HTTP_400_BAD_REQUEST
            )
        except SideDish.DoesNotExist:
            return Response(
                {"detail": "Acompanhamento não encontrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Envia notificação para o telegram
        # telegram_service = TelegramService()
        # telegram_service.send_order_notification(order)

        broadcast_open_tables()

        return Response(status=status.HTTP_200_OK)


class TicketSettlementView(APIView):
    """
    Cria um fechamento (total ou parcial) para um ticket.
    Espera payload:
    {
        "ticket_number": int,
        "total_before_additions_and_discounts": decimal,
        "additions": decimal,
        "total_amount": decimal,
        "items": [
            {"dish_order_uuid": UUID, "quantity": float},
            ...
        ]
    }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = TicketSettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: SerializedSettlementDataType = cast(
            SerializedSettlementDataType, serializer.validated_data
        )

        ticket = cast(Ticket, serializer.context.get("ticket"))
        if not ticket:
            raise ValidationError("Ticket não encontrado ou já fechado.")

        with cast(AbstractContextManager, transaction.atomic()):

            items_with_orders: list[
                tuple[SerializedSettlementItemDataType, DishOrder]
            ] = []
            for item in data["items"]:
                dish_order = DishOrder.objects.select_related("order__ticket").get(
                    uuid=item["dish_order_uuid"]
                )
                items_with_orders.append((item, dish_order))

            additions_percentage = data.get("additions_percentage") or Decimal("0")
            discounts_percentage = data.get("discounts_percentage") or Decimal("0")

            full_value = sum(
                Decimal(order.dish.price) * Decimal(str(item["dish_order_quantity"]))
                for item, order in items_with_orders
            )
            final_value = (
                full_value
                * (1 + Decimal(additions_percentage) / 100)
                * (1 - Decimal(discounts_percentage) / 100)
            )

            settlement = TicketSettlement.objects.create(
                ticket=ticket,
                settled_by=request.user,
                additions_value=full_value * Decimal(additions_percentage) / 100,
                discounts_value=full_value * Decimal(discounts_percentage) / 100,
                full_value=full_value,
                final_value=final_value,
            )

            for item, dish_order in items_with_orders:
                TicketSettlementItem.objects.create(
                    settlement=settlement,
                    dish_order=dish_order,
                    dish_order_price=dish_order.dish.price,
                    quantity=item["dish_order_quantity"],
                )

            try:
                helper = OrderHelper()
                helper.send_nfce(settlement)
            except Exception as exc:
                logger.warning("NFCE não enviada: %s", exc)

        broadcast_open_tables()

        return Response(status=status.HTTP_201_CREATED)


class OpenTablesView(APIView):
    """Retorna mesas abertas/parciais com itens e totais."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        tables = serialize_open_tables(include_items=True)
        return Response({"tables": tables}, status=status.HTTP_200_OK)
