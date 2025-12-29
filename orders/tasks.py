from __future__ import annotations

import logging
from celery import shared_task

from orders.models import Order, TicketSettlement
from printer.service import PrintService
from telegram.service import TelegramService

logger = logging.getLogger(__name__)


def _refresh_order(order_id: int) -> Order | None:
    try:
        return (
            Order.objects.select_related("ticket", "waiter")
            .prefetch_related("dish_orders__dish", "dish_orders__custom_dish")
            .get(id=order_id)
        )
    except Order.DoesNotExist:
        logger.warning("Order %s não encontrado para processamento do task.", order_id)
        return None


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_order_notification_task(self, order_id: int) -> None:
    order = _refresh_order(order_id)
    if not order:
        return

    TelegramService().send_order_notification(order)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def print_order_task(self, order_id: int) -> dict[str, object]:
    order = _refresh_order(order_id)
    if not order:
        return {"success": False, "reason": "order-not-found"}

    printer_service = PrintService()
    success, status_code, response_text = printer_service.print_order(order)
    if not success:
        logger.warning(
            "Celery: falha impressoras para pedido %s (status=%s, response=%s)",
            order_id,
            status_code,
            response_text,
        )
    return {"success": success, "status": status_code, "response": response_text}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def print_settlement_task(self, settlement_id: int) -> dict[str, object]:
    try:
        settlement = TicketSettlement.objects.select_related("ticket", "settled_by").get(
            id=settlement_id
        )
    except TicketSettlement.DoesNotExist:
        logger.warning(
            "Settlement %s não encontrado ao tentar imprimir conta.", settlement_id
        )
        return {"success": False, "reason": "settlement-not-found"}

    printer_service = PrintService()
    success, status_code, response_text = printer_service.print_bill(settlement)
    if not success:
        logger.warning(
            "Celery: falha impressoras para fechamento %s (status=%s, response=%s)",
            settlement_id,
            status_code,
            response_text,
        )
    return {"success": success, "status": status_code, "response": response_text}
