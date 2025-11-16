from django.contrib import admin

from .models import Category, Dish, SideDish, SideDishOption


class BaseMenuAdmin(admin.ModelAdmin):
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(BaseMenuAdmin):
    list_display = ("name", "color", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(SideDish)
class SideDishAdmin(BaseMenuAdmin):
    list_display = ("name", "is_available", "created_at")
    list_filter = ("is_available",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(SideDishOption)
class SideDishOptionAdmin(BaseMenuAdmin):
    list_display = (
        "display_side_dishes",
        "default_side_dish",
        "side_dish_count",
        "created_at",
    )
    filter_horizontal = ("side_dishes",)
    search_fields = ("side_dishes__name",)
    ordering = ("-created_at",)

    @admin.display(description="Qtd. acompanhamentos")
    def side_dish_count(self, obj):
        return obj.side_dishes.count()

    @admin.display(description="Acompanhamentos")
    def display_side_dishes(self, obj):
        return ", ".join(
            obj.side_dishes.order_by("name").values_list("name", flat=True)
        )


@admin.register(Dish)
class DishAdmin(BaseMenuAdmin):
    list_display = (
        "name",
        "category",
        "department",
        "price",
        "is_available",
        "created_at",
    )
    list_filter = ("category", "department", "is_available")
    list_select_related = ("category",)
    search_fields = ("name", "category__name", "ncm__code")
    autocomplete_fields = ("ncm",)
    filter_horizontal = ("side_dish_options",)
    ordering = ("name",)
