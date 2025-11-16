import requests
from typing import Literal


class TelegramClient:

    def __init__(self):
        self.token = "7641995639:AAEi5W_XRqoo-0y3u2YU4JVmTy_IrZttJPo"
        self.kitchen_chat_id = "-1002290593897"
        self.general_chat_id = "-1002411830546"

    def send_message(
        self, send_to_chat: Literal["kitchen", "general"], message: str
    ) -> requests.Response:
        if send_to_chat == "kitchen":
            chat_id = self.kitchen_chat_id
        elif send_to_chat == "general":
            chat_id = self.general_chat_id
        else:
            raise ValueError("Invalid send_to value")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&parse_mode=HTML&text={message}"
        response = requests.get(url)

        return response
