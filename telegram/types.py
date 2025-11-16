from typing import TypedDict


class DishData(TypedDict):
    dish_name: str
    department: str


class OrderDishData(TypedDict):
    dish: DishData
    amount: int | float
    dish_note: str | None


class OrderData(TypedDict):
    id: int | str
    date_time: str
    table_number: int | str
    order_dishes: list[OrderDishData]
    order_note: str | None
    waiter: str
    is_outside: bool
