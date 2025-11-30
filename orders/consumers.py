from __future__ import annotations

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from orders.selectors import serialize_open_tables


class OpenTablesConsumer(AsyncJsonWebsocketConsumer):
    """Consumer responsável por enviar a lista de mesas em aberto em tempo real."""

    group_name = "open_tables"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._send_open_tables()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Permite que o cliente solicite manualmente uma atualização.
        if content.get("type") == "refresh":
            await self._send_open_tables()

    async def open_tables_updated(self, event):
        await self.send_json({"event": "open_tables", "tables": event["tables"]})

    async def _send_open_tables(self):
        await self.send_json({
            "event": "open_tables",
            "tables": await self._get_open_tables(),
        })

    @database_sync_to_async
    def _get_open_tables(self):
        return serialize_open_tables(include_items=True)
