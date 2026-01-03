from __future__ import annotations

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from orders.consumers import OpenTablesConsumer
from orders.helpers import OrderHelper
from orders.models import TicketSettlement
from orders.selectors import serialize_open_tables, serialize_settlement_history

logger = logging.getLogger(__name__)


def broadcast_open_tables() -> None:
    """
    Envia atualização das mesas abertas/parciais para o grupo de websocket.
    Ignora silenciosamente se não houver camada de canais configurada.
    """

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    async_to_sync(channel_layer.group_send)(
        OpenTablesConsumer.group_name,
        {
            "type": "open_tables_updated",
            "tables": serialize_open_tables(include_items=True),
            "history": serialize_settlement_history(),
        },
    )


def cancel_ticket_settlement(settlement: TicketSettlement, justification: str) -> None:
    justification = (justification or "").strip()
    if len(justification) < 15:
        raise ValueError("A justificativa deve ter pelo menos 15 caracteres.")
    if settlement.canceled:
        raise ValueError("Este fechamento já está cancelado.")
    required_fields = (
        "nfce_access_key",
        "nfce_authorization_protocol",
        "nfce_emitter_cnpj",
        "nfce_emitter_uf",
    )
    missing_fields = [field for field in required_fields if not getattr(settlement, field)]
    if missing_fields:
        raise ValueError("Dados fiscais ausentes para cancelamento.")

    helper = OrderHelper()
    with transaction.atomic():
        try:
            response = helper.cancel_nfce(settlement, justification)
        except ValueError as exc:
            raise ValueError(str(exc))

        raw_response = None
        status_code = ""
        message = ""
        success = False
        if isinstance(response, dict):
            raw_response = response.get("raw_response")
            status_code = response.get("status_code") or ""
            message = response.get("message") or ""
            success = response.get("success", False)
        else:
            raw_response = response

        readable_response = None
        if raw_response:
            if isinstance(raw_response, (bytes, bytearray)):
                readable_response = raw_response.decode("utf-8", errors="ignore")
            else:
                readable_response = str(raw_response)

        if not success:
            logger.error(
                (
                    "Falha ao cancelar NFC-e para fechamento %s: status=%s msg=%s "
                    "payload=%s"
                ),
                settlement.id,
                status_code,
                message,
                readable_response,
            )
            raise ValueError(message or "Falha ao cancelar NFC-e; fechamento não foi cancelado.")

        cancelation_xml = None
        if readable_response:
            cancelation_xml = readable_response

        for item in settlement.items.select_related("dish_order"):
            dish_order = item.dish_order
            dish_order.quantity += item.quantity
            dish_order.save(update_fields=["quantity", "updated_at"])

        settlement.canceled = True
        settlement.cancelation_xml = cancelation_xml
        settlement.save(update_fields=["canceled", "cancelation_xml", "updated_at"])
        settlement.ticket.refresh_status_from_orders()
        transaction.on_commit(lambda: broadcast_open_tables())
