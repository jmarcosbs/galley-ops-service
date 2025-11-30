from printer.client import PrinterClient
from printer.types import (
    PrinterOrderInputType,
    PrinterOrderDishData,
    PrinterDishData,
)
from orders.models import Order


class PrintService:
    def __init__(self):
        self.client = PrinterClient()

    def print_order(self, order: Order) -> tuple[bool, int, str]:

        def _build_order_input(department: str) -> PrinterOrderInputType | None:
            items: list[PrinterOrderDishData] = []
            for dish_order in order.dish_orders.select_related("dish").filter(
                dish__department=department
            ):
                items.append(
                    {
                        "dish": PrinterDishData(
                            dish_name=dish_order.dish.name,
                            department=dish_order.dish.department,
                        ),
                        "amount": dish_order.quantity,
                        "dish_note": dish_order.note,
                    }
                )

            if not items:
                return None

            return PrinterOrderInputType(
                id=order.id,
                date_time=order.created_at.isoformat(),
                table_number=order.ticket.number,
                order_dishes=list(items),
                order_note=order.note,
                waiter=order.waiter.username,
                is_outside=False,
            )

        input_for_kitchen = _build_order_input("kitchen")
        input_for_bar = _build_order_input("bar")

        response_kitchen = (
            self.client.print_kitchen(input_for_kitchen) if input_for_kitchen else None
        )
        response_bar = self.client.print_bar(input_for_bar) if input_for_bar else None

        responses = [resp for resp in (response_kitchen, response_bar) if resp]
        success = all(resp.status_code == 200 for resp in responses) if responses else True
        primary_response = response_kitchen or response_bar
        status_code = primary_response.status_code if primary_response else 200
        response_text = primary_response.text if primary_response else ""

        return (success, status_code, response_text)
