# Tipos de input para impressão de pedidos
from datetime import datetime
from typing import Literal, TypedDict
from uuid import UUID


class SideDishData(TypedDict):
    uuid: UUID
    name: str


class DishData(TypedDict):
    uuid: UUID
    name: str
    department: Literal["kitchen", "bar"]
    amount: float
    dish_note: str | None
    side_dishes: list[SideDishData]


class PrinterOrderInputType(TypedDict):
    id: int
    created_at: datetime
    waiter_name: str
    ticket_number: int
    general_note: str | None
    dishes: list[DishData]
