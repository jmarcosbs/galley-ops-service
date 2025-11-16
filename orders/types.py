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
