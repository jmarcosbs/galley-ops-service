from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "orders"
    verbose_name = "Pedidos"

    def ready(self):
        from orders import signals  # noqa: F401
