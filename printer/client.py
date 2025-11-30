import os
import requests
from printer.types import PrinterBillInputType, PrinterOrderInputType


class PrinterClient:
    def __init__(self):
        self.base_url = (os.environ.get("PRINTER_SERVER_URL") or "").rstrip("/")
        token = os.environ.get("PRINTER_TOKEN")
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def _post(self, path: str, payload: dict) -> requests.Response:
        url = f"{self.base_url}{path}"
        return requests.post(url, headers=self.headers, json=payload, timeout=10)

    def health(self) -> requests.Response:
        url = f"{self.base_url}/health"
        return requests.get(url, headers=self.headers, timeout=5)

    def print_bar(self, order_payload: PrinterOrderInputType) -> requests.Response:
        return self._post("/print-bar", order_payload)

    def print_kitchen(self, order_payload: PrinterOrderInputType) -> requests.Response:
        return self._post("/print-kitchen", order_payload)

    def print_bill(self, bill_payload: PrinterBillInputType) -> requests.Response:
        return self._post("/print-bill", bill_payload)
