from django.urls import path

from orders.views import (
    OpenTablesView,
    OrderView,
    TicketItemAddView,
    TicketItemIncreaseView,
    TicketItemRemoveView,
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
    path("open-tables/", OpenTablesView.as_view(), name="open-tables"),
]
