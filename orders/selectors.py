from __future__ import annotations

from typing import Any

from orders.models import Ticket, TicketSettlement, TicketStatus


def _ticket_items(ticket: Ticket) -> list[dict[str, Any]]:
    """Itens restantes (ainda não liquidados) agrupados por ticket."""

    items = []
    orders_qs = ticket.orders.prefetch_related(
        "dish_orders__dish", "dish_orders__custom_dish"
    ).filter(
        dish_orders__quantity__gt=0
    )
    for dish_order in orders_qs.values_list(
        "dish_orders__uuid",
        "dish_orders__quantity",
        "dish_orders__note",
        "dish_orders__dish__name",
        "dish_orders__dish__price",
        "dish_orders__dish__department",
        "dish_orders__custom_dish__name",
        "dish_orders__custom_dish__price",
        "dish_orders__custom_dish__department",
    ):
        (
            dish_order_uuid,
            quantity,
            note,
            dish_name,
            dish_price,
            dish_department,
            custom_name,
            custom_price,
            custom_department,
        ) = dish_order
        name = dish_name or custom_name
        price = dish_price if dish_price is not None else custom_price
        department = dish_department or custom_department
        items.append(
            {
                "uuid": str(dish_order_uuid),
                "name": name,
                "quantity": float(quantity),
                "note": note,
                "price": float(price),
                "department": department,
            }
        )
    return items


def _ticket_total(items: list[dict[str, Any]]) -> float:
    return round(sum(item["price"] * item["quantity"] for item in items), 2)


def serialize_open_tables(include_items: bool = False) -> list[dict[str, Any]]:
    """Retorna dados das mesas em aberto/parcial para uso no websocket e API."""

    tickets = (
        Ticket.objects.filter(
            status__in=[TicketStatus.OPEN, TicketStatus.PARTIALLY_CLOSED]
        )
        .order_by("number")
        .prefetch_related("orders__dish_orders__dish")
    )

    serialized = []
    for ticket in tickets:
        items = _ticket_items(ticket) if include_items else []
        ticket_data = {
            "uuid": str(ticket.uuid),
            "number": ticket.number,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "total": _ticket_total(items) if include_items else None,
            "items": items if include_items else None,
        }
        serialized.append(ticket_data)

    return serialized


def serialize_settlement_history(limit: int = 10) -> list[dict[str, Any]]:
    """Retorna os últimos fechamentos de conta."""

    settlements = (
        TicketSettlement.objects.select_related("ticket", "settled_by")
        .order_by("-created_at")[:limit]
    )

    history: list[dict[str, Any]] = []
    for settlement in settlements:
        settled_by = settlement.settled_by.get_full_name() or settlement.settled_by.username
        history.append(
            {
                "uuid": str(settlement.uuid),
                "ticket_number": settlement.ticket.number,
                "final_value": float(settlement.final_value),
                "additions_value": float(settlement.additions_value),
                "discounts_value": float(settlement.discounts_value),
                "settled_by": settled_by,
                "created_at": settlement.created_at.isoformat(),
            }
        )
    return history
