import requests
from typing import Literal
import os


class TelegramClient:

    def __init__(self):
        # strip() evita falhas caso o .env tenha espaços ao redor do '='
        self.token = os.environ.get("TELEGRAM_TOKEN")
        self.kitchen_chat_id = os.environ.get("KITCHEN_CHAT_ID")
        self.general_chat_id = os.environ.get("GENERAL_CHAT_ID")

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
