import os
import requests
from printer.types import PrinterOrderInputType


class PrinterClient:
    def __init__(self):
        self.base_url = os.environ.get("PRINTER_SERVER_URL")
        self.token = os.environ.get("PRINTER_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def send_order_to_printer(
        self, printer_order_input_data: PrinterOrderInputType
    ) -> requests.Response:
        response = requests.post(
            self.base_url, headers=self.headers, json=printer_order_input_data
        )
        return response
