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
            for dish_order in order.dish_orders.select_related("dish", "custom_dish").all():
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

        response_kitchen = (
            self.client.print_kitchen(input_for_kitchen) if input_for_kitchen else None
        )
        response_bar = self.client.print_bar(input_for_bar) if input_for_bar else None

        responses = [resp for resp in (response_kitchen, response_bar) if resp]
        success = (
            all(resp.status_code == 202 for resp in responses) if responses else True
        )
        primary_response = response_kitchen or response_bar
        status_code = primary_response.status_code if primary_response else 202
        response_text = primary_response.text if primary_response else ""

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
        if settlement.nfce_xml:
            payload["access_key"] = settlement.nfce_xml
        if settlement.total_taxes:
            payload["total_taxes"] = str(settlement.total_taxes)

        response = self.client.print_bill(payload)
        success = response.status_code == 202
        return (success, response.status_code, response.text)
