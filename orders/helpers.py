from nfce.client import NFeClient
from orders.models import TicketSettlement


class OrderHelper:

    def __init__(self):
        self.nfce_client = NFeClient()

    def send_nfce(self, settlement: TicketSettlement) -> None:

        # Verifica se o sistema está disponível
        if not self.nfce_client.status_servico():
            raise Exception("Sistema de NFCE não está disponível")

        # Envia a NFCE
        # self.nfce_client.send_nfce(settlement)
