from __future__ import annotations

from typing import Any

from orders.models import Ticket, TicketStatus


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
        "dish_orders__custom_dish__name",
        "dish_orders__custom_dish__price",
    ):
        (
            dish_order_uuid,
            quantity,
            note,
            dish_name,
            dish_price,
            custom_name,
            custom_price,
        ) = dish_order
        name = dish_name or custom_name
        price = dish_price if dish_price is not None else custom_price
        items.append(
            {
                "uuid": str(dish_order_uuid),
                "name": name,
                "quantity": float(quantity),
                "note": note,
                "price": float(price),
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
