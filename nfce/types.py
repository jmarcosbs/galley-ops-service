from typing import Literal, TypedDict, Optional, Decimal, NotRequired, Tuple, Union
from lxml import etree
import requests


class ServiceStatusResponseType(TypedDict):
    ambient_type: Literal[1, 2]  # 1 - Produção, 2 - Homologação
    app_version: str  # versão da aplicação SEFAZ
    service_status: int  # status do serviço
    service_status_message: str  # mensagem do status do serviço
    uf_code: int  # código da UF
    reception_datetime: str  # data e hora de recebimento
    response_time: int  # tempo de resposta em segundos


class FiscalProductType(TypedDict):
    codigo: str
    descricao: str
    ncm: str
    cfop: str
    unidade_comercial: str
    ean: str
    ean_tributavel: str
    quantidade_comercial: Decimal
    valor_unitario_comercial: Decimal
    valor_total_bruto: Decimal
    unidade_tributavel: str
    quantidade_tributavel: Decimal
    valor_unitario_tributavel: Decimal
    outras_despesas_acessorias: Optional[Decimal]
    desconto: Optional[Decimal]


class NFe(TypedDict):
    access_key: str
    protocol: str
    justification: str
    sequence: NotRequired[int]


class CancelNFeResponseType(TypedDict):
    success: bool
    status_code: str
    message: str
    protocol: Optional[str]
    raw_response: bytes


ConsultNFeResponseType = bytes

AutorizacaoSyncSuccess = Tuple[int, etree._Element]
AutorizacaoAsyncSuccess = Tuple[int, str, etree._Element]
AutorizacaoFailure = Tuple[int, requests.Response, etree._Element]
AutorizacaoResponse = Union[
    AutorizacaoSyncSuccess, AutorizacaoAsyncSuccess, AutorizacaoFailure
]


class SendNFCESyncSuccess(TypedDict):
    success: Literal[True]
    mode: Literal["sync"]
    proc_xml: etree._Element


class SendNFCEAsyncSuccess(TypedDict):
    success: Literal[True]
    mode: Literal["async"]
    receipt: str
    nota_fiscal: etree._Element


class SendNFCEFailure(TypedDict):
    success: Literal[False]
    response: requests.Response
    nota_fiscal: etree._Element


SendNFCEResponse = Union[
    SendNFCESyncSuccess,
    SendNFCEAsyncSuccess,
    SendNFCEFailure,
]
