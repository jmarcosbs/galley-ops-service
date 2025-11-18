from django.urls import path

from orders.views import OrderView, TicketSettlementView

urlpatterns = [
    path("order/", OrderView.as_view(), name="order"),
    path(
        "ticket-settlement/", TicketSettlementView.as_view(), name="ticket-settlement"
    ),
]
