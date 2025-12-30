import os
import requests
from printer.types import (
    PrinterBillInputType,
    PrinterOrderInputType,
    PrinterSuccessResponseType,
    PrinterErrorResponseType,
    PrinterSuccessHealthResponseType,
    PrinterErrorResponseHealthType,
)


class PrinterClient:
    def __init__(self):
        self.base_url = (os.environ.get("PRINTER_SERVER_URL") or "").rstrip("/")
        # token = os.environ.get("PRINTER_TOKEN")
        # envia o content type nos headers
        self.headers = {"Content-Type": "application/json"}

    def _post(self, path: str, payload: dict) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code >= 500:
            # Padroniza mensagem de erro do driver para não vazar detalhes internos
            message = "Erro no servidor da impressora"
            try:
                data = response.json()
                message = data.get("detail") or message
            except ValueError:
                if response.text:
                    message = response.text
            raise requests.HTTPError(message, response=response)
        return response

    def health(
        self,
    ) -> PrinterSuccessHealthResponseType | PrinterErrorResponseHealthType:
        url = f"{self.base_url}/health"
        return requests.get(url, timeout=10)

    def print_bar(
        self, order_payload: PrinterOrderInputType
    ) -> PrinterSuccessResponseType | PrinterErrorResponseType:
        return self._post("/print-bar", order_payload)

    def print_kitchen(
        self, order_payload: PrinterOrderInputType
    ) -> PrinterSuccessResponseType | PrinterErrorResponseType:
        return self._post("/print-kitchen", order_payload)

    def print_bill(
        self, bill_payload: PrinterBillInputType
    ) -> PrinterSuccessResponseType | PrinterErrorResponseType:
        return self._post("/print-bill", bill_payload)
