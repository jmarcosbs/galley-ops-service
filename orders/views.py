from contextlib import AbstractContextManager
from decimal import Decimal
from typing import Any, cast

from django.db import transaction
from django.shortcuts import get_object_or_404
from nfce.models import NCM
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.models import Dish, SideDish, CustomDish
from orders.helpers import OrderHelper
from orders.selectors import serialize_open_tables
from orders.serializers import (
    OrderSerializer,
    TicketItemAddSerializer,
    TicketItemIncreaseSerializer,
    TicketItemRemoveSerializer,
    TicketSettlementSerializer,
    TicketSettlementCancelSerializer,
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
from printer.service import PrintService
from orders.types import (
    SerializedOrderDataType,
    SerializedSettlementDataType,
    SerializedSettlementItemDataType,
)
import logging

logger = logging.getLogger(__name__)


def _create_dish_order_from_payload(
    order: Order, dish_data: dict[str, Any]
) -> DishOrder:
    """
    Cria um DishOrder (e relacionamentos) a partir de dados validados do serializer.
    """
    if dish_data.get("dish_uuid"):
        dish = Dish.objects.get(uuid=dish_data["dish_uuid"])
        dish_order = DishOrder.objects.create(
            order=order,
            dish=dish,
            quantity=dish_data["amount"],
            note=dish_data.get("dish_note"),
        )

        for side_dish_data in dish_data.get("side_dishes", []):
            side_dish = SideDish.objects.get(uuid=side_dish_data["side_dish_uuid"])
            option = dish.side_dish_options.filter(side_dishes=side_dish).first()
            if not option:
                raise ValidationError(
                    f"Acompanhamento {side_dish} não disponível para {dish}."
                )
            DishOrderSideDish.objects.create(
                dish_order=dish_order, option=option, side_dish=side_dish
            )
    else:
        custom_data = dish_data["custom_dish"]
        ncm = NCM.objects.get(code=custom_data["ncm"])

        custom_dish = CustomDish.objects.create(
            name=custom_data["name"],
            price=custom_data["price"],
            ncm=ncm,
            department=custom_data["department"],
        )

        dish_order = DishOrder.objects.create(
            order=order,
            custom_dish=custom_dish,
            quantity=dish_data["amount"],
            note=dish_data.get("dish_note"),
        )

    return dish_order


class OrderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        user = request.user

        # printa o payload recebido
        print(request.data)

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
        is_outside = serialized_order_data.get("is_outside", False)

        order: Order | None = None

        try:
            with cast(AbstractContextManager, transaction.atomic()):
                ticket = Ticket.objects.filter(
                    number=ticket_number,
                    status__in=[TicketStatus.OPEN, TicketStatus.PARTIALLY_CLOSED],
                ).first()

                if not ticket:
                    ticket = Ticket.objects.create(
                        number=ticket_number,
                        created_by=user,
                        status=TicketStatus.OPEN,
                        is_outside=is_outside,
                    )
                elif ticket.status == TicketStatus.CLOSED:
                    raise ValidationError("Este ticket já está fechado.")
                else:
                    if ticket.is_outside != is_outside:
                        ticket.is_outside = is_outside
                        ticket.save(update_fields=["is_outside", "updated_at"])

                order = Order.objects.create(
                    ticket=ticket,
                    waiter=user,
                    note=serialized_order_data.get("general_note"),
                )

                for dish_data in serialized_order_data["dishes"]:
                    _create_dish_order_from_payload(order, dish_data)

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

        if order:
            try:
                printer_service = PrintService()
                success, printer_status, printer_response = printer_service.print_order(
                    order
                )
                if not success:
                    logger.warning(
                        "Falha ao enviar pedido %s para impressoras (status=%s, response=%s)",
                        order.id,
                        printer_status,
                        printer_response,
                    )
            except (
                Exception
            ) as exc:  # pragma: no cover - fallback para evitar quebrar pedidos
                logger.exception(
                    "Erro ao enviar pedido %s para impressoras: %s", order.id, exc
                )

        return Response(status=status.HTTP_200_OK)


class TicketItemAddView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = TicketItemAddSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                "Payload inválido ao adicionar item: %s | data=%s",
                serializer.errors,
                request.data,
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket = cast(Ticket, serializer.context.get("ticket"))
        if not ticket:
            raise ValidationError("Ticket não encontrado ou já fechado.")

        dish_data = dict(serializer.validated_data)
        dish_data.pop("ticket_number", None)

        dish_order: DishOrder | None = None
        try:
            with cast(AbstractContextManager, transaction.atomic()):
                order = Order.objects.create(
                    ticket=ticket,
                    waiter=request.user,
                    note=None,
                )
                dish_order = _create_dish_order_from_payload(order, dish_data)

        except ValidationError as exc:
            return Response(
                {"detail": exc.detail if hasattr(exc, "detail") else str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Dish.DoesNotExist:
            return Response(
                {"detail": "Prato não encontrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except SideDish.DoesNotExist:
            return Response(
                {"detail": "Acompanhamento não encontrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        broadcast_open_tables()

        return Response(
            {
                "detail": "Item adicionado com sucesso.",
                "item_uuid": str(dish_order.uuid) if dish_order else None,
            },
            status=status.HTTP_201_CREATED,
        )


class TicketItemRemoveView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = TicketItemRemoveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket = cast(Ticket, serializer.context.get("ticket"))
        dish_order = cast(DishOrder, serializer.context.get("dish_order"))
        quantity = serializer.validated_data["quantity"]

        with cast(AbstractContextManager, transaction.atomic()):
            dish_order.quantity -= quantity
            dish_order.save(update_fields=["quantity", "updated_at"])
            ticket.refresh_status_from_orders()
            transaction.on_commit(lambda: broadcast_open_tables())

        return Response(
            {
                "detail": "Item removido com sucesso.",
                "remaining_quantity": dish_order.quantity,
            },
            status=status.HTTP_200_OK,
        )


class TicketItemIncreaseView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = TicketItemIncreaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket = cast(Ticket, serializer.context.get("ticket"))
        dish_order = cast(DishOrder, serializer.context.get("dish_order"))
        quantity = serializer.validated_data["quantity"]

        with cast(AbstractContextManager, transaction.atomic()):
            dish_order.quantity += quantity
            dish_order.save(update_fields=["quantity", "updated_at"])
            ticket.refresh_status_from_orders()
            transaction.on_commit(lambda: broadcast_open_tables())

        return Response(
            {
                "detail": "Quantidade atualizada com sucesso.",
                "current_quantity": dish_order.quantity,
            },
            status=status.HTTP_200_OK,
        )


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

            additions_percentage = data["additions_percentage"]
            discounts_percentage = data.get("discounts_percentage") or Decimal("0")

            # Printa os itens e valores
            print("Itens e valores:")
            for item, order in items_with_orders:
                dish = order.dish_or_custom_dish
                print(
                    f"Item: {item['dish_order_uuid']}, Quantidade: {item['dish_order_quantity']}, Valor: {Decimal(dish.price) * Decimal(str(item['dish_order_quantity']))}"
                )

            full_value = sum(
                Decimal(order.dish_or_custom_dish.price)
                * Decimal(str(item["dish_order_quantity"]))
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
                dish = dish_order.dish_or_custom_dish
                TicketSettlementItem.objects.create(
                    settlement=settlement,
                    dish_order=dish_order,
                    dish_order_price=dish.price,
                    quantity=item["dish_order_quantity"],
                )

            helper = OrderHelper()
            try:
                response = helper.send_nfce(settlement)
            except ValidationError:
                raise
            except Exception:
                logger.exception(
                    "Erro ao emitir NFC-e para fechamento %s", settlement.id
                )
                raise
            if not response or not response.get("success"):
                logger.error(
                    "Falha na emissão da NFC-e para fechamento %s, abortando fechamento.",
                    settlement.id,
                )
                raise ValidationError(
                    "Falha na emissão da NFC-e; conta não foi fechada."
                )

        broadcast_open_tables()

        try:
            printer_service = PrintService()
            success, printer_status, printer_response = printer_service.print_bill(
                settlement
            )
            if not success:
                logger.warning(
                    "Falha ao enviar fechamento %s para impressora de contas (status=%s, response=%s)",
                    settlement.id,
                    printer_status,
                    printer_response,
                )
        except Exception as exc:  # pragma: no cover
            logger.exception(
                "Erro ao imprimir fechamento %s na impressora de contas: %s",
                settlement.id,
                exc,
            )

        return Response(status=status.HTTP_201_CREATED)


class TicketSettlementReprintView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, settlement_uuid: str):
        settlement = get_object_or_404(
            TicketSettlement.objects.select_related("ticket", "settled_by"),
            uuid=settlement_uuid,
        )

        printer_service = PrintService()
        try:
            success, printer_status, printer_response = printer_service.print_bill(
                settlement
            )
        except Exception as exc:  # pragma: no cover
            logger.exception(
                "Erro ao reimprimir fechamento %s na impressora de contas: %s",
                settlement.id,
                exc,
            )
            raise ValidationError("Erro ao reimprimir cupom.")

        if not success:
            logger.error(
                "Falha ao reimprimir fechamento %s (status=%s, response=%s)",
                settlement.id,
                printer_status,
                printer_response,
            )
            raise ValidationError(
                "Não foi possível reimprimir o cupom. Tente novamente em instantes."
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class OpenTablesView(APIView):
    """Retorna mesas abertas/parciais com itens e totais."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        tables = serialize_open_tables(include_items=True)
        return Response({"tables": tables}, status=status.HTTP_200_OK)


class TicketSettlementCancelView(APIView):
    """
    Cancela um fechamento.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        if not request.user.is_superuser:
            raise ValidationError(
                "Apenas superusuários podem cancelar fechamentos."
            )

        serializer = TicketSettlementCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        settlement = cast(TicketSettlement, serializer.context.get("settlement"))
        justification = cast(str, serializer.validated_data["justification"])

        with cast(AbstractContextManager, transaction.atomic()):
            helper = OrderHelper()
            try:
                response = helper.cancel_nfce(settlement, justification)
            except ValueError as exc:
                raise ValidationError(str(exc))

            if not response or not response.get("success"):
                logger.error(
                    "Falha ao cancelar NFC-e para fechamento %s, abortando cancelamento.",
                    settlement.id,
                )
                raise ValidationError(
                    "Falha ao cancelar NFC-e; fechamento não foi cancelado."
                )

            raw_response = response.get("raw_response") if isinstance(response, dict) else None
            cancelation_xml = None
            if raw_response:
                if isinstance(raw_response, (bytes, bytearray)):
                    cancelation_xml = raw_response.decode("utf-8", errors="ignore")
                else:
                    cancelation_xml = str(raw_response)

            for item in settlement.items.select_related("dish_order"):
                dish_order = item.dish_order
                dish_order.quantity += item.quantity
                dish_order.save(update_fields=["quantity", "updated_at"])

            settlement.canceled = True
            settlement.cancelation_xml = cancelation_xml
            settlement.save(update_fields=["canceled", "cancelation_xml", "updated_at"])
            settlement.ticket.refresh_status_from_orders()
            transaction.on_commit(lambda: broadcast_open_tables())

        return Response(status=status.HTTP_204_NO_CONTENT)
