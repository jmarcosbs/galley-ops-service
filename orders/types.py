from decimal import Decimal
from typing import TypedDict
from uuid import UUID


class SerializedSideDishDataType(TypedDict):
    side_dish_uuid: UUID


class SerializedDishOrderDataType(TypedDict):
    dish_uuid: UUID
    amount: float
    dish_note: str | None
    side_dishes: list[SerializedSideDishDataType]


class SerializedOrderDataType(TypedDict):
    ticket: int
    dishes: list[SerializedDishOrderDataType]
    general_note: str | None
    is_outside: bool


class SerializedSettlementItemDataType(TypedDict):
    dish_order_uuid: UUID
    dish_order_quantity: float


class SerializedSettlementDataType(TypedDict):
    ticket_number: int
    is_outside: bool
    additions_percentage: Decimal
    discounts_percentage: Decimal | None
    items: list[SerializedSettlementItemDataType]
