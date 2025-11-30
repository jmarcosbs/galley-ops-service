from django.urls import path

from orders.consumers import OpenTablesConsumer


websocket_urlpatterns = [
    path("ws/open-tables/", OpenTablesConsumer.as_asgi()),
]
