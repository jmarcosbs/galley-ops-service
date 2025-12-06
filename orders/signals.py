from __future__ import annotations

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from orders.models import Ticket
from orders.services import broadcast_open_tables


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, **kwargs):
    transaction.on_commit(broadcast_open_tables)


@receiver(post_delete, sender=Ticket)
def ticket_post_delete(sender, instance, **kwargs):
    transaction.on_commit(broadcast_open_tables)
