from pynfe.processamento.comunicacao import ComunicacaoSefaz

certificado = "Certificado 2025.pfx"
senha = 'avaifc9669'
uf = 'sc'
homologacao = True

chave_acesso = '42251001597994000138650010000001211807061004'
con = ComunicacaoSefaz(uf, certificado, senha, homologacao)
envio = con.consulta_nota('nfce', chave_acesso) # nfe ou nfce
print(envio.text.encode('utf-8')) # SEFAZ SP utilizar envio.content