from django.contrib import admin

from .models import (
    DishOrder,
    DishOrderSideDish,
    Order,
    Ticket,
    TicketSettlement,
    TicketSettlementItem,
)


class BaseOrderAdmin(admin.ModelAdmin):
    readonly_fields = ("uuid", "created_at", "updated_at")


class DishOrderSideDishInline(admin.TabularInline):
    model = DishOrderSideDish
    extra = 0
    autocomplete_fields = ("option", "side_dish")


class DishOrderInline(admin.TabularInline):
    model = DishOrder
    extra = 0
    show_change_link = True
    autocomplete_fields = ("dish",)


class TicketSettlementItemInline(admin.TabularInline):
    model = TicketSettlementItem
    extra = 0
    readonly_fields = ("dish_order_price",)
    autocomplete_fields = ("dish_order",)
    show_change_link = True


@admin.register(Order)
class OrderAdmin(BaseOrderAdmin):
    list_display = ("ticket", "waiter", "dish_count", "created_at", "updated_at")
    list_filter = ("waiter", "created_at")
    search_fields = (
        "ticket__number",
        "uuid",
        "waiter__username",
        "waiter__first_name",
        "waiter__last_name",
    )
    autocomplete_fields = ("waiter",)
    list_select_related = ("ticket", "waiter")
    inlines = (DishOrderInline,)

    @admin.display(description="Qtd. pratos")
    def dish_count(self, obj):
        return obj.dish_orders.count()


@admin.register(DishOrder)
class DishOrderAdmin(BaseOrderAdmin):
    list_display = ("dish", "order", "quantity", "created_at")
    search_fields = ("uuid", "dish__name", "order__ticket__number")
    list_select_related = ("order", "dish")
    autocomplete_fields = ("order", "dish")
    inlines = (DishOrderSideDishInline,)


@admin.register(Ticket)
class TicketAdmin(BaseOrderAdmin):
    list_display = ("number", "status", "created_by", "orders_count", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("number", "uuid", "orders__uuid")
    autocomplete_fields = ("created_by",)
    list_select_related = ("created_by",)

    @admin.display(description="Qtd. pedidos")
    def orders_count(self, obj):
        return obj.orders.count()


@admin.register(TicketSettlement)
class TicketSettlementAdmin(BaseOrderAdmin):
    list_display = (
        "ticket",
        "final_value",
        "full_value",
        "additions_value",
        "discounts_value",
        "total_taxes",
        "settled_by",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("ticket__number", "uuid")
    autocomplete_fields = ("ticket", "settled_by")
    inlines = (TicketSettlementItemInline,)
    readonly_fields = BaseOrderAdmin.readonly_fields + ("total_taxes",)


@admin.register(TicketSettlementItem)
class TicketSettlementItemAdmin(BaseOrderAdmin):
    list_display = (
        "settlement",
        "dish_order",
        "quantity",
        "dish_order_price",
        "total_taxes",
    )
    search_fields = ("uuid", "settlement__ticket__number", "dish_order__uuid")
    list_select_related = ("settlement", "dish_order")
    autocomplete_fields = ("settlement", "dish_order")
    readonly_fields = BaseOrderAdmin.readonly_fields + ("total_taxes",)
