from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from orders.consumers import OpenTablesConsumer
from orders.selectors import serialize_open_tables, serialize_settlement_history


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
