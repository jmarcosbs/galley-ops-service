from printer.client import PrinterClient
from printer.types import DishData, PrinterOrderInputType
from orders.models import Order


class PrintService:
    def __init__(self):
        self.client = PrinterClient()

    def print_order(self, order: Order) -> tuple[bool, int, str]:

        input_data_for_printer = PrinterOrderInputType(
            id=order.id,
            created_at=order.created_at.isoformat(),
            waiter_name=order.waiter.name,
            ticket_number=order.ticket.number,
            general_note=str(order.note),
            dishes=list[DishData](
                [
                    {
                        "uuid": dish.uuid,
                        "name": dish.name,
                        "department": dish.department,
                        "amount": dish.amount,
                        "dish_note": dish.dish_note,
                        "side_dishes": [
                            {
                                "uuid": side_dish.uuid,
                                "name": side_dish.name,
                            }
                            for side_dish in dish.side_dishes.all()
                        ],
                    }
                    for dish in order.dishes.all()
                ]
            ),
        )

        response = self.client.send_order_to_printer(input_data_for_printer)
        return response.status_code == 200, response.status_code, response.text
