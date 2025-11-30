from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from orders.models import Ticket
from orders.selectors import serialize_open_tables


def _broadcast_open_tables_after_commit():
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    def _send():
        async_to_sync(channel_layer.group_send)(
            "open_tables",
            {
                "type": "open_tables_updated",
                "tables": serialize_open_tables(),
            },
        )

    transaction.on_commit(_send)


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, **kwargs):
    _broadcast_open_tables_after_commit()


@receiver(post_delete, sender=Ticket)
def ticket_post_delete(sender, instance, **kwargs):
    _broadcast_open_tables_after_commit()
