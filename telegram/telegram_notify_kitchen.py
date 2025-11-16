from datetime import datetime
import requests  # Import the requests module

def send_notification_kitchen(order_data):
    
    # Agora você pode acessar os dados do pedido
    order_id = order_data['id']
    
    original_date_time = order_data['date_time']
    # Converter a string para um objeto datetime
    date_object = datetime.fromisoformat(original_date_time[:-2] + "00")  # Remove o 'Z' no final
    # Formatar a data no formato desejado
    date_time = date_object.strftime("%d-%m-%Y %H:%M:%S")

    table_number = order_data['table_number']
    order_dishes = order_data['order_dishes']
    order_note = order_data['order_note']
    waiter = order_data['waiter']
    is_outside = order_data['is_outside']
    
    dishes_text = ""
    
    for order_dish in order_dishes:
        dish = order_dish['dish']
        amount = order_dish['amount']
        dish_note = order_dish['dish_note']
        dishes_text += f"""

        <b>🍽️ {amount}x {dish['dish_name']}</b>
        {'Observação: ' + dish_note if dish_note else ''}
        """
    
    telegram_message = f"""

        <b>🛎️ Pedido {order_id}</b>\n
        📅 Data: {date_time}
        👨‍🦲 Atendente: {waiter}
        🪑 Mesa: {'R' if is_outside else ''}{table_number}
        
        {dishes_text}
        
        {'📄 Observação geral: ' + order_note if order_note else ''}

    """
    
    token = "7641995639:AAEi5W_XRqoo-0y3u2YU4JVmTy_IrZttJPo"
    
    chatIdKitchen = "-1002290593897"
    
    telegramUrlKitchen = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatIdKitchen}&parse_mode=HTML&text={telegram_message}"
    

    isForKitchen = False

    for order_dish in order_dishes:
        dish = order_dish['dish']
        if dish['department'] == 'cozinha':
            isForKitchen = True
    
    if isForKitchen:
        send = requests.get(telegramUrlKitchen)  # Send message in Telegram
        send.json()

    
    print("Notificação enviada cozinha")
