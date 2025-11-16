from django.contrib import admin

from .models import DishOrder, DishOrderSideDish, Order


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


@admin.register(Order)
class OrderAdmin(BaseOrderAdmin):
    list_display = ("ticket", "waiter", "dish_count", "created_at", "updated_at")
    list_filter = ("waiter", "created_at")
    search_fields = (
        "ticket",
        "uuid",
        "waiter__username",
        "waiter__first_name",
        "waiter__last_name",
    )
    autocomplete_fields = ("waiter",)
    inlines = (DishOrderInline,)

    @admin.display(description="Qtd. pratos")
    def dish_count(self, obj):
        return obj.dish_orders.count()


@admin.register(DishOrder)
class DishOrderAdmin(BaseOrderAdmin):
    list_display = ("dish", "order", "quantity", "created_at")
    search_fields = ("uuid", "dish__name", "order__ticket")
    list_select_related = ("order", "dish")
    autocomplete_fields = ("order", "dish")
    inlines = (DishOrderSideDishInline,)
