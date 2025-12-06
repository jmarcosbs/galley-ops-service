from datetime import timezone as dt_timezone

from django.utils import timezone

from printer.client import PrinterClient
from printer.types import (
    PrinterOrderInputType,
    PrinterOrderDishData,
    PrinterDishData,
    PrinterBillInputType,
)
from orders.models import Order, TicketSettlement


class PrintService:
    def __init__(self):
        self.client = PrinterClient()

    @staticmethod
    def _format_datetime(dt) -> str:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_default_timezone())
        dt = dt.astimezone(dt_timezone.utc)
        iso = dt.isoformat(timespec="milliseconds")
        if iso.endswith("+00:00"):
            iso = iso[:-6] + "Z"
        return iso

    def print_order(self, order: Order) -> tuple[bool, int, str]:

        def _build_order_input(department: str) -> PrinterOrderInputType | None:
            items: list[PrinterOrderDishData] = []
            for dish_order in order.dish_orders.select_related(
                "dish", "custom_dish"
            ).all():
                item = dish_order.dish_or_custom_dish
                if not item or item.department != department:
                    continue
                items.append(
                    {
                        "dish": PrinterDishData(
                            dish_name=item.name,
                            department=item.department,
                        ),
                        "amount": dish_order.quantity,
                        "dish_note": dish_order.note,
                    }
                )

            if not items:
                return None

            return PrinterOrderInputType(
                id=order.id,
                date_time=self._format_datetime(order.created_at),
                table_number=order.ticket.number,
                order_dishes=list(items),
                order_note=order.note,
                waiter=order.waiter.username,
                is_outside=False,
            )

        input_for_kitchen = _build_order_input("kitchen")
        input_for_bar = _build_order_input("bar")

        print(input_for_kitchen)

        responses: list = []
        errors: list[str] = []

        def _safe_print(send_fn, payload, label: str):
            if not payload:
                return
            try:
                response = send_fn(payload)
                responses.append(response)
            except Exception as exc:  # pragma: no cover - log/propagate aggregated
                errors.append(f"{label}: {exc}")

        _safe_print(self.client.print_kitchen, input_for_kitchen, "kitchen")
        _safe_print(self.client.print_bar, input_for_bar, "bar")

        success = (
            not errors and all(resp.status_code == 202 for resp in responses)
            if responses
            else not errors
        )

        primary_response = responses[0] if responses else None
        if primary_response:
            status_code = primary_response.status_code
            response_parts = [primary_response.text] if primary_response.text else []
        else:
            status_code = 202 if success else 500
            response_parts = []

        if errors:
            response_parts.append("; ".join(errors))

        response_text = " | ".join(part for part in response_parts if part)

        return (success, status_code, response_text)

    def print_bill(self, settlement: TicketSettlement) -> tuple[bool, int, str]:
        ticket = settlement.ticket
        settlement_items = settlement.items.select_related(
            "dish_order__dish",
            "dish_order__custom_dish",
        )

        dishes = []
        for settlement_item in settlement_items:
            dish_order = settlement_item.dish_order
            item = dish_order.dish_or_custom_dish
            if not item:
                continue
            dishes.append(
                {
                    "dish": PrinterDishData(
                        dish_name=item.name,
                        department=item.department,
                    ),
                    "amount": settlement_item.quantity,
                    "dish_note": dish_order.note,
                    "unit_price": float(settlement_item.dish_order_price),
                }
            )

        if not dishes:
            return (True, 202, "")

        payload: PrinterBillInputType = PrinterBillInputType(
            id=ticket.id,
            date_time=self._format_datetime(settlement.created_at),
            table_number=ticket.number,
            order_dishes=dishes,
            order_note="",
            waiter=settlement.settled_by.username,
            is_outside=False,
            total=float(settlement.full_value),
            amount_to_pay=float(settlement.final_value),
        )

        adjustments = float(settlement.additions_value - settlement.discounts_value)
        if adjustments:
            payload["service"] = adjustments

        if settlement.nfce_qrcode_url:
            payload["qr_url"] = settlement.nfce_qrcode_url
        if settlement.nfce_access_key:
            payload["access_key"] = settlement.nfce_access_key
        elif settlement.nfce_xml:
            # Mantém fallback para registros antigos que não possuem chave armazenada.
            payload["access_key"] = settlement.nfce_xml
        if settlement.nfce_access_key_url:
            payload["access_key_url"] = settlement.nfce_access_key_url
        if settlement.nfce_number:
            payload["nfce_number"] = settlement.nfce_number
        if settlement.nfce_series:
            payload["nfce_series"] = settlement.nfce_series
        if settlement.nfce_authorization_protocol:
            payload["protocol"] = settlement.nfce_authorization_protocol
        if settlement.nfce_authorization_datetime:
            payload["protocol_datetime"] = self._format_datetime(
                settlement.nfce_authorization_datetime
            )
        if settlement.total_taxes:
            payload["total_taxes"] = str(settlement.total_taxes)

        response = self.client.print_bill(payload)
        success = response.status_code == 202
        return (success, response.status_code, response.text)
