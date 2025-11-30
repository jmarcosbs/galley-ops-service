import logging

try:
    from nfce.client import NFeClient
except ImportError:  # optional dependency
    NFeClient = None  # type: ignore

from orders.models import TicketSettlement

logger = logging.getLogger(__name__)


class OrderHelper:

    def __init__(self):
        self.nfce_client = NFeClient() if NFeClient else None

    def send_nfce(self, settlement: TicketSettlement) -> None:

        if not self.nfce_client:
            logger.info("NFCE client não configurado; pulando envio.")
            return

        # Verifica se o sistema está disponível
        if not self.nfce_client.status_servico():
            raise Exception("Sistema de NFCE não está disponível")

        # Envia a NFCE
        # self.nfce_client.send_nfce(settlement)
