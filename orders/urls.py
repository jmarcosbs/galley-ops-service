from django.urls import path

from orders.views import (
    OpenTablesView,
    OrderView,
    TicketItemAddView,
    TicketItemIncreaseView,
    TicketItemRemoveView,
    TicketSettlementReprintView,
    TicketSettlementView,
)

urlpatterns = [
    path("order/", OrderView.as_view(), name="order"),
    path(
        "ticket-items/add/",
        TicketItemAddView.as_view(),
        name="ticket-item-add",
    ),
    path(
        "ticket-items/remove/",
        TicketItemRemoveView.as_view(),
        name="ticket-item-remove",
    ),
    path(
        "ticket-items/increase/",
        TicketItemIncreaseView.as_view(),
        name="ticket-item-increase",
    ),
    path(
        "ticket-settlement/", TicketSettlementView.as_view(), name="ticket-settlement"
    ),
    path(
        "ticket-settlement/<uuid:settlement_uuid>/reprint/",
        TicketSettlementReprintView.as_view(),
        name="ticket-settlement-reprint",
    ),
    path("open-tables/", OpenTablesView.as_view(), name="open-tables"),
]
