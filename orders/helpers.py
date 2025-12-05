import logging
from typing import Optional

from nfce.services import NFCeService
from nfce.types import SendNFCEResponse, ServiceStatusResponseType
from orders.models import TicketSettlement

logger = logging.getLogger(__name__)


class OrderHelper:
    def __init__(self) -> None:
        try:
            self.nfce_service: Optional[NFCeService] = NFCeService()
        except Exception as exc:
            logger.warning("NFCE service não pôde ser inicializado: %s", exc)
            self.nfce_service = None

    def _check_service(self) -> tuple[bool, Optional[ServiceStatusResponseType]]:
        if not self.nfce_service:
            return False, None
        status = self.nfce_service.status_servico()
        logger.info(
            "Status SEFAZ retorno: ambiente=%s status=%s msg=%s",
            status.get("ambient_type"),
            status.get("service_status"),
            status.get("service_status_message"),
        )
        # cStat 107 = Serviço em Operação
        is_available = status.get("service_status") == "107"
        return is_available, status

    def send_nfce(self, settlement: TicketSettlement) -> Optional[SendNFCEResponse]:
        """
        Emite NFC-e para um fechamento, em modo normal quando o serviço está
        disponível ou em contingência quando indisponível.
        """
        if not self.nfce_service:
            logger.info("NFCE service não configurado; pulando envio.")
            return None

        logger.info("Iniciando emissão NFC-e para fechamento %s", settlement.id)
        is_available, status = self._check_service()
        is_contingency = not is_available
        contingency_message = None
        if is_contingency:
            status_message = status.get("service_status_message") if status else ""
            contingency_message = (
                status_message or "Serviço da SEFAZ indisponível - contingência"
            )
            logger.warning(
                "Emitindo em contingência para fechamento %s: status=%s msg=%s",
                settlement.id,
                status.get("service_status") if status else None,
                status_message,
            )

        nfce = self.nfce_service.create_nfce(
            settlement, is_contingency=is_contingency
        )
        response = self.nfce_service.send_nfce(
            nfce,
            settlement,
            is_contingency=is_contingency,
            contingency_message=contingency_message,
        )
        logger.info(
            "Finalizada emissão NFC-e para fechamento %s: sucesso=%s",
            settlement.id,
            response["success"] if response else None,
        )
        return response
