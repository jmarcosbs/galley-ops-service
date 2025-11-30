# Tipos de payload aceitos pela API do driver de impressão
from typing import Literal, NotRequired, TypedDict


class PrinterDishData(TypedDict):
    dish_name: str
    department: Literal["bar", "kitchen"]


class PrinterOrderDishData(TypedDict):
    dish: PrinterDishData
    amount: float
    dish_note: str | None


class PrinterOrderInputType(TypedDict):
    id: int
    date_time: str
    table_number: int
    order_dishes: list[PrinterOrderDishData]
    order_note: str
    waiter: str
    is_outside: bool


class PrinterBillDishData(PrinterOrderDishData):
    unit_price: float


class PrinterBillInputType(PrinterOrderInputType):
    order_dishes: list[PrinterBillDishData]
    total: float
    amount_to_pay: float
    service: NotRequired[float]
    company_name: NotRequired[str]
    company_address: NotRequired[str]
    company_cnpj: NotRequired[str]
    company_ie: NotRequired[str]
    access_key: NotRequired[str]
    qr_number: NotRequired[str]
    qr_url: NotRequired[str]
    nfce_number: NotRequired[str]
    nfce_series: NotRequired[str]
    protocol: NotRequired[str]
    protocol_datetime: NotRequired[str]
    total_taxes: NotRequired[str]
    md5: NotRequired[str]


class PrinterResponseType(TypedDict):
    status_code: int
    response: str
