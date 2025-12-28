from django.contrib import admin, messages
from lxml import etree
from pynfe.utils.flags import NAMESPACE_NFE
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from nfce.services import NFCeService

from .models import (
    DishOrder,
    DishOrderSideDish,
    Order,
    Ticket,
    TicketSettlement,
    TicketSettlementItem,
)


class BaseTicketAreaFilter(admin.SimpleListFilter):
    title = "Área"
    parameter_name = "ticket_area"
    related_field: str = ""

    def lookups(self, request, model_admin):
        return (
            ("inside", "Salão"),
            ("outside", "Área externa"),
        )

    def queryset(self, request, queryset):
        if not self.value() or not self.related_field:
            return queryset

        is_outside = self.value() == "outside"
        return queryset.filter(**{self.related_field: is_outside})


class OrderTicketAreaFilter(BaseTicketAreaFilter):
    related_field = "ticket__is_outside"


class DishOrderTicketAreaFilter(BaseTicketAreaFilter):
    related_field = "order__ticket__is_outside"


class TicketSettlementAreaFilter(BaseTicketAreaFilter):
    related_field = "ticket__is_outside"


class TicketSettlementItemAreaFilter(BaseTicketAreaFilter):
    related_field = "settlement__ticket__is_outside"


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
    autocomplete_fields = ("dish", "custom_dish")


class TicketSettlementItemInline(admin.TabularInline):
    model = TicketSettlementItem
    extra = 0
    readonly_fields = ("dish_order_price", "charged_half_portion")
    autocomplete_fields = ("dish_order",)
    show_change_link = True


@admin.register(Order)
class OrderAdmin(BaseOrderAdmin):
    list_display = ("ticket_label", "waiter", "dish_count", "created_at", "updated_at")
    list_filter = ("waiter", "created_at", OrderTicketAreaFilter)
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

    @admin.display(description="Mesa")
    def ticket_label(self, obj):
        return obj.ticket.table_label

    @admin.display(description="Qtd. pratos")
    def dish_count(self, obj):
        return obj.dish_orders.count()


@admin.register(DishOrder)
class DishOrderAdmin(BaseOrderAdmin):
    list_display = ("display_item", "ticket_label", "order", "quantity", "created_at")
    search_fields = (
        "uuid",
        "dish__name",
        "custom_dish__name",
        "order__ticket__number",
    )
    list_filter = ("created_at", DishOrderTicketAreaFilter)
    list_select_related = ("order__ticket", "dish", "custom_dish")
    autocomplete_fields = ("order", "dish", "custom_dish")
    inlines = (DishOrderSideDishInline,)

    @admin.display(description="Item")
    def display_item(self, obj):
        return obj.dish or obj.custom_dish

    @admin.display(description="Mesa")
    def ticket_label(self, obj):
        return obj.order.ticket.table_label


@admin.register(Ticket)
class TicketAdmin(BaseOrderAdmin):
    list_display = (
        "table_label",
        "number",
        "is_outside",
        "status",
        "created_by",
        "orders_count",
        "created_at",
    )
    list_filter = ("status", "is_outside", "created_at")
    search_fields = ("number", "uuid", "orders__uuid")
    autocomplete_fields = ("created_by",)
    list_select_related = ("created_by",)

    @admin.display(description="Mesa")
    def table_label(self, obj):
        return obj.table_label

    @admin.display(description="Qtd. pedidos")
    def orders_count(self, obj):
        return obj.orders.count()


@admin.register(TicketSettlement)
class TicketSettlementAdmin(ExtraButtonsMixin, BaseOrderAdmin):
    list_display = (
        "ticket_label",
        "final_value",
        "full_value",
        "additions_value",
        "discounts_value",
        "is_partial",
        "total_taxes",
        "settled_by",
        "created_at",
    )
    list_filter = ("created_at", TicketSettlementAreaFilter)
    search_fields = ("ticket__number", "uuid")
    autocomplete_fields = ("ticket", "settled_by")
    list_select_related = ("ticket", "settled_by")
    inlines = (TicketSettlementItemInline,)
    readonly_fields = BaseOrderAdmin.readonly_fields + (
        "total_taxes",
        "nfce_last_status_code",
        "nfce_last_status_message",
        "nfce_last_consult_payload",
    )
    actions = ("consult_nfce",)

    @admin.display(description="Mesa")
    def ticket_label(self, obj):
        return obj.ticket.table_label

    @staticmethod
    def _extract_status_from_xml(payload: str) -> tuple[str, str]:
        try:
            root = etree.fromstring(
                payload.encode("utf-8") if isinstance(payload, str) else payload
            )
            ns = {"nfe": NAMESPACE_NFE}
            status_code = root.xpath("string(//nfe:cStat)", namespaces=ns)
            status_message = root.xpath("string(//nfe:xMotivo)", namespaces=ns)
            return status_code or "", status_message or ""
        except Exception:
            return "", ""

    def _consult_and_store(self, request, queryset):
        service = NFCeService()
        updated = 0

        for settlement in queryset:
            if not settlement.nfce_access_key:
                self.message_user(
                    request,
                    f"{settlement} sem chave de acesso NFC-e; consulta ignorada.",
                    messages.WARNING,
                )
                continue

            response = service.consult_nfe(settlement.nfce_access_key)
            payload_str = (
                response.decode("utf-8", errors="ignore")
                if isinstance(response, (bytes, bytearray))
                else str(response)
            )
            status_code, status_message = self._extract_status_from_xml(payload_str)

            settlement.nfce_last_consult_payload = payload_str
            settlement.nfce_last_status_code = status_code
            settlement.nfce_last_status_message = status_message
            settlement.save(
                update_fields=[
                    "nfce_last_consult_payload",
                    "nfce_last_status_code",
                    "nfce_last_status_message",
                    "updated_at",
                ]
            )
            updated += 1

        if updated:
            self.message_user(
                request, f"{updated} NFC-e consultada(s) com sucesso.", messages.SUCCESS
            )
        return updated

    def consult_nfce(self, request, queryset):
        self._consult_and_store(request, queryset)

    consult_nfce.short_description = "Consultar NFC-e na SEFAZ"

    @button(
        change_form=True,
        html_attrs={"class": "btn btn-success"},
        label="Consultar NFC-e",
    )
    def consult_nfce_button(self, request, pk):
        settlement = self.get_object(request, pk)
        if not settlement:
            self.message_user(request, "Liquidação não encontrada.", messages.ERROR)
            return
        if not settlement.nfce_access_key:
            self.message_user(
                request, "Liquidação sem chave NFC-e; consulta ignorada.", messages.ERROR
            )
            return
        self._consult_and_store(request, [settlement])


@admin.register(TicketSettlementItem)
class TicketSettlementItemAdmin(BaseOrderAdmin):
    list_display = (
        "settlement",
        "ticket_label",
        "dish_order",
        "quantity",
        "charged_half_portion",
        "dish_order_price",
        "total_taxes",
    )
    list_filter = (TicketSettlementItemAreaFilter,)
    search_fields = ("uuid", "settlement__ticket__number", "dish_order__uuid")
    list_select_related = ("settlement__ticket", "dish_order")
    autocomplete_fields = ("settlement", "dish_order")
    readonly_fields = BaseOrderAdmin.readonly_fields + ("total_taxes",)

    @admin.display(description="Mesa")
    def ticket_label(self, obj):
        return obj.settlement.ticket.table_label
