from datetime import datetime
from telegram.client import TelegramClient
from orders.models import Order
from menu.models import DepartmentChoices


class TelegramService:
    def __init__(self):
        self.client = TelegramClient()

    def make_dishes_text_list(self, order_dishes: list[dict]) -> str:
        dishes_text = ""
        for order_dish in order_dishes:
            dish = getattr(order_dish, "dish", None)
            custom_dish = getattr(order_dish, "custom_dish", None)
            amount = order_dish.quantity
            dish_note = order_dish.note
            dish_name = ""

            if dish:
                dish_name = dish.name
            elif custom_dish:
                dish_name = custom_dish.name
            else:
                dish_name = "Item sem nome"

            dishes_text += f"""
            <b>{amount}x {dish_name}</b>
            {'<b>Observação: </b>' + dish_note if dish_note else ''}
            """
        return dishes_text

    def make_telegram_order_message(
        self,
        order_id: int,
        date_time: str,
        waiter: str,
        table_number: int,
        order_note: str | None,
        dishes_text: str,
    ) -> str:

        return f"""

            <b>🛎️ Pedido {order_id}</b>\n
            <b>Data:</b> {date_time}
            <b>Atendente:</b> {waiter}
            <b>Mesa:</b> {table_number}
            
            {dishes_text}
            
            {'<b>Observação geral:</b> ' + order_note if order_note else ''}

        """

    def send_order_notification(self, order: Order) -> None:

        # Agora você pode acessar os dados do pedido
        order_id = order.id

        original_date_time = order.created_at
        # Converter a string para um objeto datetime
        date_object = datetime.fromisoformat(
            original_date_time.isoformat()[:-2] + "00"
        )  # Remove o 'Z' no final
        # Formatar a data no formato desejado
        date_time = date_object.strftime("%d-%m-%Y %H:%M:%S")

        ticket_number = order.ticket.number
        general_note = order.note
        waiter = order.waiter.username

        should_send_to_kitchen = False

        for dish_order in order.dish_orders.all():
            department = None
            if dish_order.dish:
                department = dish_order.dish.department
            elif dish_order.custom_dish:
                department = dish_order.custom_dish.department

            if department == DepartmentChoices.KITCHEN:
                should_send_to_kitchen = True
                break

        if should_send_to_kitchen:
            kitchen_response = self.client.send_message(
                send_to_chat="kitchen",
                message=self.make_telegram_order_message(
                    order_id,
                    date_time,
                    waiter,
                    ticket_number,
                    str(general_note),
                    self.make_dishes_text_list(order.dish_orders.all()),
                ),
            )
            if kitchen_response.status_code != 200:
                print(
                    f"Erro ao enviar notificação para a cozinha: {kitchen_response.text}"
                )

        general_response = self.client.send_message(
            send_to_chat="general",
            message=self.make_telegram_order_message(
                order_id,
                date_time,
                waiter,
                ticket_number,
                str(general_note),
                self.make_dishes_text_list(order.dish_orders.all()),
            ),
        )

        if general_response.status_code != 200:
            print(f"Erro ao enviar notificação para o geral: {general_response.text}")
