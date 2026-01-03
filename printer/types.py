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
    subtotal: float
    service_fee: float
    final_value: float
    access_key_url: NotRequired[str]
    company_name: NotRequired[str]
    company_address: NotRequired[str]
    company_cnpj: NotRequired[str]
    company_ie: NotRequired[str]
    access_key: NotRequired[str]
    qr_url: NotRequired[str]
    nfce_number: NotRequired[str]
    nfce_series: NotRequired[str]
    emission_datetime: NotRequired[str]
    authorization_protocol: NotRequired[str]
    authorization_datetime: NotRequired[str]
    total_taxes: NotRequired[str]
    md5: NotRequired[str]


class PrinterSuccessResponseType(TypedDict):
    message: str


class PrinterErrorResponseType(TypedDict):
    detail: str


class PrinterDashboardSummaryInputType(TypedDict):
    start_date: str
    end_date: str
    total_additions: float
    total_tables: int
    printed_at: str


class PrinterSuccessHealthResponseType(TypedDict):
    status: str


class PrinterErrorResponseHealthType(TypedDict):
    detail: str
