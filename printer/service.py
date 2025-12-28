import os
from datetime import timezone as dt_timezone

from django.utils import timezone

from printer.client import PrinterClient
from printer.types import (
    PrinterOrderInputType,
    PrinterOrderDishData,
    PrinterDishData,
    PrinterBillInputType,
)
from orders.models import Order, TicketSettlement


class PrintService:
    def __init__(self):
        self.client = PrinterClient()
        self.company_data = self._build_company_data()

    @staticmethod
    def _format_datetime(dt) -> str:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_default_timezone())
        dt = dt.astimezone(dt_timezone.utc)
        iso = dt.isoformat(timespec="milliseconds")
        if iso.endswith("+00:00"):
            iso = iso[:-6] + "Z"
        return iso

    def print_order(self, order: Order) -> tuple[bool, int, str]:

        def _build_order_input(department: str) -> PrinterOrderInputType | None:
            dish_orders = order.dish_orders.select_related(
                "dish", "dish__category", "custom_dish"
            ).all()

            items_with_sort: list[tuple[tuple[int, int], PrinterOrderDishData]] = []
            for position, dish_order in enumerate(dish_orders):
                item = dish_order.dish_or_custom_dish
                if not item or item.department != department:
                    continue

                category = getattr(item, "category", None)
                category_name = getattr(category, "name", None)
                is_starter = (
                    department == "kitchen"
                    and category_name
                    and "entrada" in category_name.casefold()
                )

                items_with_sort.append(
                    (
                        (0 if is_starter else 1, position),
                        {
                            "dish": PrinterDishData(
                                dish_name=item.name,
                                department=item.department,
                            ),
                            "amount": dish_order.quantity,
                            "dish_note": dish_order.note,
                        },
                    )
                )

            sorted_items = sorted(items_with_sort, key=lambda entry: entry[0])
            items = [printer_dish for _, printer_dish in sorted_items]

            if not items:
                return None

            return PrinterOrderInputType(
                id=order.id,
                date_time=self._format_datetime(order.created_at),
                table_number=order.ticket.number,
                order_dishes=list(items),
                order_note=str(order.note),
                waiter=order.waiter.username,
                is_outside=order.ticket.is_outside,
            )

        input_for_kitchen = _build_order_input("kitchen")
        input_for_bar = _build_order_input("bar")

        print(input_for_kitchen)

        responses: list = []
        errors: list[str] = []

        def _safe_print(send_fn, payload, label: str):
            if not payload:
                return
            try:
                response = send_fn(payload)
                responses.append(response)
            except Exception as exc:  # pragma: no cover - log/propagate aggregated
                errors.append(f"{label}: {exc}")

        _safe_print(self.client.print_kitchen, input_for_kitchen, "kitchen")
        _safe_print(self.client.print_bar, input_for_bar, "bar")

        success = (
            not errors and all(resp.status_code == 202 for resp in responses)
            if responses
            else not errors
        )

        primary_response = responses[0] if responses else None
        if primary_response:
            status_code = primary_response.status_code
            response_parts = [primary_response.text] if primary_response.text else []
        else:
            status_code = 202 if success else 500
            response_parts = []

        if errors:
            response_parts.append("; ".join(errors))

        response_text = " | ".join(part for part in response_parts if part)

        return (success, status_code, response_text)

    def print_bill(self, settlement: TicketSettlement) -> tuple[bool, int, str]:
        ticket = settlement.ticket
        settlement_items = settlement.items.select_related(
            "dish_order__dish",
            "dish_order__dish__category",
            "dish_order__custom_dish",
        )

        # Agrupa pratos idênticos para impressão da conta, independente das observações.
        grouped_dishes: dict[tuple[str, str, str], dict] = {}
        for position, settlement_item in enumerate(settlement_items):
            dish_order = settlement_item.dish_order
            item = dish_order.dish_or_custom_dish
            if not item:
                continue

            category = getattr(item, "category", None)
            category_name = getattr(category, "name", None)
            department = item.department
            item_id = dish_order.dish_id or dish_order.custom_dish_id
            if item_id is None:
                continue

            display_quantity = (
                0.65
                if getattr(settlement_item, "charged_half_portion", False)
                else settlement_item.quantity
            )
            key = (
                "dish" if dish_order.dish_id else "custom",
                str(item_id),
                str(settlement_item.dish_order_price),
            )
            note = (dish_order.note or "").strip()

            grouped = grouped_dishes.get(key)
            if grouped is None:
                grouped_dishes[key] = {
                    "dish": PrinterDishData(
                        dish_name=item.name,
                        department=department,
                    ),
                    "amount": display_quantity,
                    "notes": [note] if note else [],
                    "unit_price": float(settlement_item.dish_order_price),
                    "category_name": category_name,
                    "department": department,
                    "first_seen_index": position,
                }
            else:
                grouped["amount"] += display_quantity
                if note and note not in grouped["notes"]:
                    grouped["notes"].append(note)
                grouped["first_seen_index"] = min(
                    grouped["first_seen_index"], position
                )

        # Ordena entradas primeiro, depois principais e por fim itens da copa.
        def _group_order(entry: dict) -> tuple[int, int]:
            category_name = entry.get("category_name")
            department = entry.get("department")
            if category_name and "entrada" in category_name.casefold():
                bucket = 1
            elif department == "bar":
                bucket = 3
            else:
                bucket = 2
            return (bucket, entry.get("first_seen_index", 0))

        dishes = []
        for grouped in sorted(grouped_dishes.values(), key=_group_order):
            notes = grouped.get("notes") or []
            dishes.append(
                {
                    "dish": grouped["dish"],
                    "amount": grouped["amount"],
                    "dish_note": " | ".join(notes) if notes else None,
                    "unit_price": grouped["unit_price"],
                }
            )

        if not dishes:
            return (True, 202, "")

        payload: PrinterBillInputType = PrinterBillInputType(
            id=ticket.id,
            date_time=self._format_datetime(settlement.created_at),
            table_number=ticket.number,
            order_dishes=dishes,
            order_note="",
            waiter=settlement.settled_by.username,
            is_outside=ticket.is_outside,
            subtotal=float(str(settlement.full_value)),
            service_fee=float(str(settlement.additions_value)),
            final_value=float(str(settlement.final_value)),
        )

        payload.update(self.company_data)

        if settlement.nfce_qrcode_url:
            payload["qr_url"] = str(settlement.nfce_qrcode_url)
        if settlement.nfce_access_key:
            payload["access_key"] = str(settlement.nfce_access_key)
        elif settlement.nfce_xml:
            # Mantém fallback para registros antigos que não possuem chave armazenada.
            payload["access_key"] = str(settlement.nfce_xml)
        if settlement.nfce_access_key_url:
            payload["access_key_url"] = str(settlement.nfce_access_key_url)
        if settlement.nfce_number:
            payload["nfce_number"] = str(settlement.nfce_number)
        if settlement.nfce_series:
            payload["nfce_series"] = str(settlement.nfce_series)
        if settlement.nfce_emission_datetime:
            payload["emission_datetime"] = self._format_datetime(
                settlement.nfce_emission_datetime
            )
        if settlement.nfce_authorization_protocol:
            payload["authorization_protocol"] = str(
                settlement.nfce_authorization_protocol
            )
        if settlement.nfce_authorization_datetime:
            payload["authorization_datetime"] = self._format_datetime(
                settlement.nfce_authorization_datetime
            )
        if settlement.total_taxes:
            payload["total_taxes"] = str(settlement.total_taxes)

        response = self.client.print_bill(payload)
        success = response.status_code == 202
        return (success, response.status_code, response.text)

    @staticmethod
    def _build_company_data() -> dict[str, str]:
        company_name = (
            os.environ.get("RAZAO_SOCIAL_EMITENTE")
            or os.environ.get("NOME_FANTASIA_EMITENTE")
            or ""
        )
        street = os.environ.get("ENDERECO_LOGRADOURO_EMITENTE") or ""
        number = os.environ.get("ENDERECO_NUMERO_EMITENTE") or ""
        neighborhood = os.environ.get("ENDERECO_BAIRRO_EMITENTE") or ""
        city = os.environ.get("ENDERECO_MUNICIPIO_EMITENTE") or ""
        state = os.environ.get("ENDERECO_UF_EMITENTE") or ""

        address_parts: list[str] = []
        if street or number:
            joined = street.strip()
            if number:
                joined = f"{joined}, {number.strip()}" if joined else number.strip()
            address_parts.append(joined)
        if neighborhood:
            address_parts.append(neighborhood.strip())
        if city or state:
            city_state = city.strip()
            if state:
                city_state = f"{city_state}/{state.strip()}" if city_state else state.strip()
            address_parts.append(city_state)

        company_address = " - ".join(part for part in address_parts if part)

        return {
            "company_name": company_name,
            "company_address": company_address,
            "company_cnpj": os.environ.get("CNPJ_EMITENTE", ""),
            "company_ie": os.environ.get("INSCRICAO_ESTADUAL_EMITENTE", ""),
        }
