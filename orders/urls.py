from django.urls import path

from orders.views import OpenTablesView, OrderView, TicketSettlementView

urlpatterns = [
    path("order/", OrderView.as_view(), name="order"),
    path(
        "ticket-settlement/", TicketSettlementView.as_view(), name="ticket-settlement"
    ),
    path("open-tables/", OpenTablesView.as_view(), name="open-tables"),
]
