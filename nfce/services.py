from __future__ import annotations

import os
from typing import Optional, cast
from lxml import etree
from pynfe.processamento.comunicacao import ComunicacaoSefaz
from pynfe.utils.flags import NAMESPACE_NFE
from orders.models import TicketSettlementItem, TicketSettlement
from nfce.types import (
    ServiceStatusResponseType,
    NFe,
    CancelNFeResponseType,
    ConsultNFeResponseType,
    AutorizacaoResponse,
    AutorizacaoAsyncSuccess,
    AutorizacaoFailure,
    AutorizacaoSyncSuccess,
    SendNFCEResponse,
)
from pynfe.entidades.cliente import Cliente
from pynfe.entidades.emitente import Emitente
from pynfe.entidades.notafiscal import NotaFiscal, NotaFiscalProduto
from pynfe.entidades.fonte_dados import _fonte_dados
from pynfe.entidades.evento import EventoCancelarNota
from pynfe.processamento.serializacao import SerializacaoXML, SerializacaoQrcode
from pynfe.processamento.assinatura import AssinaturaA1
from pynfe.utils.flags import CODIGO_BRASIL
from decimal import Decimal
import datetime


class NFCeService:
    def __init__(self):
        self.certificado = os.environ.get("CERTIFICATE_LOCATION")
        self.senha = os.environ.get("CERTIFICATE_PASSWORD")
        self.uf = os.environ.get("CERTIFICATE_UF", "sc")
        self.homologacao = os.environ.get("DEBUG", "true") == "true"
        self.comunicacao_sefaz = ComunicacaoSefaz(
            self.uf, self.certificado, self.senha, self.homologacao
        )
        self.token = (
            os.environ.get("TOKEN_HOMOLOGACAO")
            if self.homologacao
            else os.environ.get("TOKEN_PRODUCAO")
        )
        self.csc = (
            os.environ.get("CSC_HOMOLOGACAO")
            if self.homologacao
            else os.environ.get("CSC_PRODUCAO")
        )

        self.emitente = Emitente(
            razao_social=os.environ.get("RAZAO_SOCIAL_EMITENTE"),
            cnpj=os.environ.get("CNPJ_EMITENTE"),
            nome_fantasia=os.environ.get("NOME_FANTASIA_EMITENTE"),
            codigo_de_regime_tributario=os.environ.get(
                "CODIGO_DE_REGIME_TRIBUTARIO_EMITENTE"
            ),
            inscricao_estadual=os.environ.get("INSCRICAO_ESTADUAL_EMITENTE"),
            endereco_logradouro=os.environ.get("ENDERECO_LOGRADOURO_EMITENTE"),
            endereco_numero=os.environ.get("ENDERECO_NUMERO_EMITENTE"),
            endereco_bairro=os.environ.get("ENDERECO_BAIRRO_EMITENTE"),
            endereco_municipio=os.environ.get("ENDERECO_MUNICIPIO_EMITENTE"),
            endereco_uf=os.environ.get("ENDERECO_UF_EMITENTE"),
            endereco_cep=os.environ.get("ENDERECO_CEP_EMITENTE"),
            endereco_pais=CODIGO_BRASIL,
        )

    def _adicionar_responsavel_tecnico(self, nota_fiscal: NotaFiscal) -> None:
        nota_fiscal.adicionar_responsavel_tecnico(
            cnpj=os.environ.get("CNPJ_RESPONSAVEL_TECNICO"),
            contato=os.environ.get("CONTATO_RESPONSAVEL_TECNICO"),
            email=os.environ.get("EMAIL_RESPONSAVEL_TECNICO"),
            fone=os.environ.get("FONE_RESPONSAVEL_TECNICO"),
        )

    def _obter_data_emissao(
        self, nfe_elemento: etree._Element
    ) -> Optional[datetime.datetime]:
        ns = {"nfe": NAMESPACE_NFE}
        valores = nfe_elemento.xpath(
            "nfe:infNFe/nfe:ide/nfe:dhEmi/text()", namespaces=ns
        )
        if not valores:
            return None
        data = valores[0]
        if data.endswith("Z"):
            data = data.replace("Z", "+00:00")
        try:
            return datetime.datetime.fromisoformat(data)
        except ValueError:
            return None

    def _adicionar_produto_servico(
        self,
        tax_note: NotaFiscal,
        settlement_item: TicketSettlementItem,
    ) -> NotaFiscalProduto:

        dish = settlement_item.dish_order.dish
        settlement = settlement_item.settlement

        if settlement.discounts_value > 0:
            Decimal(
                discount_value=(
                    settlement_item.dish_order_price
                    * settlement.discounts_value
                    / settlement.full_value
                )
            )
        else:
            discount_value = None

        if settlement.additions_value > 0:
            Decimal(
                addition_value=(
                    settlement_item.dish_order_price
                    * settlement.additions_value
                    / settlement.full_value
                )
            )
        else:
            addition_value = None

        product_tax_note = tax_note.adicionar_produto_servico(
            nota_fiscal=tax_note,
            codigo=dish.id,
            descricao=dish.name,
            ncm=dish.ncm,
            cfop="5102",
            unidade_comercial="UN",
            ean="SEM GTIN",
            ean_tributavel="SEM GTIN",
            quantidade_comercial=settlement_item.quantity,
            valor_unitario_comercial=dish.price,
            valor_total_bruto=dish.price * settlement_item.quantity,
            unidade_tributavel="UN",
            quantidade_tributavel=settlement_item.quantity,
            valor_unitario_tributavel=dish.price,
            outras_despesas_acessorias=addition_value,
            desconto=discount_value,
        )

        return product_tax_note

    def status_servico(self) -> ServiceStatusResponseType:
        xml = self.comunicacao_sefaz.status_servico("nfce")  # nfe ou nfce

        # parse do XML (xml.content é mais seguro)
        root = etree.fromstring(xml.content)

        # namespaces
        ns = {"nfe": NAMESPACE_NFE}

        # localiza o elemento retConsStatServ em qualquer lugar do XML
        ret = root.xpath("//nfe:retConsStatServ", namespaces=ns)
        if not ret:
            raise ValueError("retConsStatServ não encontrado no XML da SEFAZ")

        ret = ret[0]  # pega o primeiro nó

        # extrai os campos
        response: ServiceStatusResponseType = {
            "ambient_type": ret.findtext("{http://www.portalfiscal.inf.br/nfe}tpAmb"),
            "app_version": ret.findtext("{http://www.portalfiscal.inf.br/nfe}verAplic"),
            "service_status": ret.findtext("{http://www.portalfiscal.inf.br/nfe}cStat"),
            "service_status_message": ret.findtext(
                "{http://www.portalfiscal.inf.br/nfe}xMotivo"
            ),
            "uf_code": ret.findtext("{http://www.portalfiscal.inf.br/nfe}cUF"),
            "reception_datetime": ret.findtext(
                "{http://www.portalfiscal.inf.br/nfe}dhRecbto"
            ),
            "response_time": ret.findtext("{http://www.portalfiscal.inf.br/nfe}tMed"),
        }

        return response

    def create_nfce(
        self,
        TicketSettlement: TicketSettlement,
        is_contingency: bool = False,
        cliente: Optional[Cliente] = None,
    ) -> NotaFiscal:

        nota_fiscal = NotaFiscal(
            emitente=self.emitente,
            cliente=cliente,
            uf=self.uf.upper(),
            natureza_operacao="VENDA",  # Venda
            forma_pagamento=0,  # 0=Pagamento à vista
            tipo_pagamento=1,
            modelo=65,  # 65=NFC-e
            serie="1",
            numero_nf=TicketSettlement.id,  # Número do Documento Fiscal.
            data_emissao=datetime.datetime.now(),
            data_saida_entrada=datetime.datetime.now(),
            tipo_documento=1,  # 1=saida
            municipio="4205407",  # Código IBGE do Município
            tipo_impressao_danfe=4,  # 4=DANFE NFC-e;
            forma_emissao=(
                "1" if not is_contingency else "2"
            ),  # 1=Emissão normal 2=Contingência;
            cliente_final=1,  # 1=Consumidor final;
            indicador_destino=1,
            indicador_presencial=1,
            finalidade_emissao="1",  # 1=NF-e normal
            processo_emissao="0",  # 0=Emissão de NF-e com aplicativo do contribuinte;
            transporte_modalidade_frete=9,  # 9=Sem Ocorrência de Transporte.
            totais_tributos_aproximado=TicketSettlement.total_taxes(),
        )

        self._adicionar_responsavel_tecnico(nota_fiscal)

        for settlement_item in TicketSettlement.items.all():
            self._adicionar_produto_servico(nota_fiscal, settlement_item)

        return nota_fiscal

    def send_nfce(
        self,
        nota_fiscal: NotaFiscal,
        settlement: TicketSettlement,
        is_contingency: bool = False,
        contingency_message: Optional[str] = None,
    ) -> SendNFCEResponse:

        if is_contingency and not contingency_message:
            raise ValueError(
                "Mensagem de contingência é obrigatória quando o envio é em contingência"
            )

        # serialização
        serializador = SerializacaoXML(
            _fonte_dados,
            homologacao=self.homologacao,
            contingencia=contingency_message if is_contingency else None,
        )
        nfce = serializador.exportar()

        # assinatura
        a1 = AssinaturaA1(self.certificado, self.senha)
        xml = a1.assinar(nfce)

        # gera e adiciona o qrcode no xml NT2015/003
        xml_com_qrcode, qrcode_url = SerializacaoQrcode().gerar_qrcode(
            self.token, self.csc, xml, return_qr=True
        )
        emission_datetime = self._obter_data_emissao(xml_com_qrcode)

        envio: AutorizacaoResponse = self.comunicacao_sefaz.autorizacao(
            modelo="nfce", nota_fiscal=xml_com_qrcode
        )

        response: SendNFCEResponse

        # em caso de sucesso o retorno será o xml autorizado
        # Ps: no modo sincrono, o retorno será o xml completo (<nfeProc> = <NFe> + <protNFe>)
        # no modo async é preciso montar o nfeProc, juntando o retorno com a NFe
        if envio[0] == 0:
            # envio síncrono retorna apenas o XML autorizado
            if len(envio) == 2 and isinstance(envio[1], etree._Element):
                sync_envio = cast(AutorizacaoSyncSuccess, envio)
                proc_xml_str = (
                    etree.tostring(sync_envio[1], encoding="unicode")
                    .replace("\n", "")
                    .replace("ns0:", "")
                )
                response = {
                    "success": True,
                    "mode": "sync",
                    "proc_xml": sync_envio[1],
                }

                settlement.nfce_xml = proc_xml_str
                settlement.nfce_qrcode_url = qrcode_url
                settlement.nfce_issued_at = emission_datetime
                settlement.save(
                    update_fields=[
                        "nfce_xml",
                        "nfce_qrcode_url",
                        "nfce_issued_at",
                        "updated_at",
                    ]
                )
                print("Sucesso!")
                print(proc_xml_str)
            # envio assíncrono retorna número do recibo e xml enviado
            else:
                async_envio = cast(AutorizacaoAsyncSuccess, envio)
                nota_fiscal_str = (
                    etree.tostring(async_envio[2], encoding="unicode")
                    .replace("\n", "")
                    .replace("ns0:", "")
                )
                response = {
                    "success": True,
                    "mode": "async",
                    "receipt": async_envio[1],
                    "nota_fiscal": async_envio[2],
                }
                settlement.nfce_xml = nota_fiscal_str
                settlement.nfce_qrcode_url = qrcode_url
                settlement.nfce_issued_at = emission_datetime
                settlement.save(
                    update_fields=[
                        "nfce_xml",
                        "nfce_qrcode_url",
                        "nfce_issued_at",
                        "updated_at",
                    ]
                )
                print("Envio assíncrono recebido com sucesso!")
                print(f"Recibo: {async_envio[1]}")
        # em caso de erro o retorno será o xml de resposta da SEFAZ + NF-e enviada
        else:
            failure_envio = cast(AutorizacaoFailure, envio)
            response = {
                "success": False,
                "response": failure_envio[1],
                "nota_fiscal": failure_envio[2],
            }
            print("Erro:")
            print(failure_envio[1].text)  # resposta
            print("Nota:")
            print(etree.tostring(failure_envio[2], encoding="unicode"))  # nfe

        return response

    def cancel_nfe(self, nfe: NFe) -> CancelNFeResponseType:
        required_fields = ("access_key", "protocol", "justification")
        missing_fields = [field for field in required_fields if not nfe.get(field)]
        if missing_fields:
            raise ValueError(
                f"Os campos {', '.join(missing_fields)} são obrigatórios para o cancelamento."
            )

        evento = EventoCancelarNota()
        evento.cnpj = self.emitente.cnpj
        evento.chave = nfe["access_key"]
        evento.protocolo = nfe["protocol"]
        evento.justificativa = nfe["justification"]
        evento.n_seq_evento = int(nfe.get("sequence", 1) or 1)
        evento.uf = self.uf.upper()
        evento.data_emissao = datetime.datetime.now()

        serializador = SerializacaoXML(_fonte_dados, homologacao=self.homologacao)
        evento_xml = serializador.serializar_evento(evento)
        assinatura = AssinaturaA1(self.certificado, self.senha)
        evento_assinado = assinatura.assinar(evento_xml)
        response = self.comunicacao_sefaz.evento("nfce", evento_assinado)
        return self._parse_cancelamento_response(response)

    def consult_nfe(self, access_key: str) -> ConsultNFeResponseType:
        envio = self.comunicacao_sefaz.consulta_nota("nfce", access_key)  # nfe ou nfce
        return envio.text.encode("utf-8")  # SEFAZ SP utilizar envio.content

    def _parse_cancelamento_response(self, response) -> CancelNFeResponseType:
        raw = getattr(response, "content", b"") or getattr(response, "text", "").encode(
            "utf-8"
        )
        status_code = ""
        message = ""
        protocol: Optional[str] = None
        success = False

        if raw:
            try:
                root = etree.fromstring(raw)
                ns = f"{{{NAMESPACE_NFE}}}"
                ret_env = root.find(f".//{ns}retEnvEvento")
                tag_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
                if ret_env is None and tag_name == "retEnvEvento":
                    ret_env = root

                env_status = (
                    ret_env.findtext(f"{ns}cStat") if ret_env is not None else ""
                )
                env_message = (
                    ret_env.findtext(f"{ns}xMotivo") if ret_env is not None else ""
                )

                ret_event = (
                    ret_env.find(f"{ns}retEvento") if ret_env is not None else None
                )
                inf_event = (
                    ret_event.find(f"{ns}infEvento") if ret_event is not None else None
                )

                if inf_event is not None:
                    status_code = inf_event.findtext(f"{ns}cStat") or env_status or ""
                    message = inf_event.findtext(f"{ns}xMotivo") or env_message or ""
                    protocol = inf_event.findtext(f"{ns}nProt")
                else:
                    status_code = env_status or ""
                    message = env_message or ""
                success = status_code in {"101", "135", "155"}
            except etree.XMLSyntaxError:
                message = "Não foi possível processar o retorno da SEFAZ."

        return {
            "success": success,
            "status_code": status_code,
            "message": message,
            "protocol": protocol,
            "raw_response": raw,
        }
