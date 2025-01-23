from models import *
import xml.etree.ElementTree as ET
import xmltodict


dict_modalidade_saque = {
    'Parcelado':'2',
}


def consulta_saque_complementar_bmg(retorno_login,dict_infos):
    login = 'ROBO.56306'
    senha = r'irWY!kQD@6%rb'
    if dict_infos.get("id_consulta_massa") and not dict_infos.get('leads_saque'):
        print('aguardando consulta em massa BMG')
        time.sleep(randint(10,30))
    cartoes = []
    #vem no dict
    url = "https://ws1.bmgconsig.com.br/webservices/SaqueComplementar?wsdl"
    cpf = dict_infos.get('cpf')
    print('matricula',dict_infos.get('matricula'))
    matricula = dict_infos.get('matricula','-')
    codigos_entidade = {'1581':'RMC','4277':'RCC'}
    # Define the SOAP envelope XML
    msg_retorno = ''
    for codigo in codigos_entidade.keys():
        print(codigo)
        soap_envelope = fr"""
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://webservice.econsig.bmg.com">
        <soapenv:Header/>
        <soapenv:Body>
            <web:buscarCartoesDisponiveis soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <param xsi:type="web:CartaoDisponivelParameter">
                    <login xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{login}</login>
                    <senha xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{senha}</senha>
                    <codigoEntidade xsi:type="xsd:int">{codigo}</codigoEntidade>
                    <cpf xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{cpf}</cpf>
                </param>
            </web:buscarCartoesDisponiveis>
        </soapenv:Body>
        </soapenv:Envelope>
        """
        # Define the headers
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "Content-Length": str(len(soap_envelope)),
            "SOAPAction": "http://webservice.econsig.bmg.com/buscarCartoesDisponiveis",  # Replace with the appropriate SOAP action
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
        }

 
        response = requests.post(url, data=soap_envelope, headers=headers)
        soap_response_content = response.content
            # Parse the SOAP response content
        root = ET.fromstring(soap_response_content)
        # Find the faultcode and faultstring
        faultstring = ''
        for elem in root.iter():
            if "faultstring" in elem.tag:
                faultstring = elem.text

        if 'Ocorreu um erro ao validar o acesso do usuário' in faultstring:
            print('login inválido')
            alert_desenvolvimento(f'LOGIN INVÁLIDO BMG API, {faultstring}')
            return {'sucesso':False,'msg_retorno':'API Indisponível','obs':unidecode('API Indisponível'),'obs':'API Indisponível'}
        elif faultstring:
            print(faultstring)
            try:
                fault_msg = faultstring.split('ServiceException:')[-1]
            except:
                fault_msg = faultstring
            if 'could not find deserializer' in fault_msg:
                fault_msg = 'Não foi possível consultar'
            cartoes.append({'tipo_cartao':codigos_entidade[codigo],'msg_retorno':fault_msg})
            continue

        dict = xmltodict.parse(response.content)
        
        formas_envio = []
        cartao_info = dict['soapenv:Envelope']['soapenv:Body']['ns1:buscarCartoesDisponiveisResponse']['buscarCartoesDisponiveisReturn']['cartoesRetorno']['cartoesRetorno']
        try:
            liberado = cartao_info['liberado']['#text'] if '#text' in cartao_info['liberado'] else None
            numero_cartao = cartao_info['numeroCartao']['#text'] if '#text' in cartao_info['numeroCartao'] else None
            numero_adesao = cartao_info['numeroAdesao']['#text'] if '#text' in cartao_info['numeroAdesao'] else None
            numero_conta_interna = cartao_info['numeroContaInterna']['#text'] if '#text' in cartao_info['numeroContaInterna'] else None
            tipo_saque = cartao_info['modalidadeSaque']['#text'] if '#text' in cartao_info['modalidadeSaque'] else None

            cartoes.append({
                'matricula': matricula,
                'liberado': bool(liberado.lower() == 'true'),
                'numero_cartao': numero_cartao,
                'numero_adesao': numero_adesao,
                'numero_conta_interna': numero_conta_interna,
                'tipo_saque':tipo_saque,
                'tipo_cartao':codigos_entidade[codigo],
                'codigo_entidade':codigo

            })
        except:
            for n in cartao_info:
                liberado = n['liberado']['#text'] if '#text' in n['liberado'] else None
                numero_cartao = n['numeroCartao']['#text'] if '#text' in n['numeroCartao'] else None
                numero_adesao = n['numeroAdesao']['#text'] if '#text' in n['numeroAdesao'] else None
                numero_conta_interna = n['numeroContaInterna']['#text'] if '#text' in n['numeroContaInterna'] else None
                tipo_saque = n['modalidadeSaque']['#text'] if '#text' in n['modalidadeSaque'] else None
                cartoes.append({
                    'matricula': matricula,
                    'liberado': liberado,
                    'numero_cartao': numero_cartao,
                    'numero_adesao': numero_adesao,
                    'numero_conta_interna': numero_conta_interna,
                    'tipo_saque':tipo_saque,
                    'tipo_cartao':codigos_entidade[codigo],
                })
                
        print(dict['soapenv:Envelope']['soapenv:Body']['ns1:buscarCartoesDisponiveisResponse']['buscarCartoesDisponiveisReturn']['formasEnvio']['formasEnvio'])
        for forma in dict['soapenv:Envelope']['soapenv:Body']['ns1:buscarCartoesDisponiveisResponse']['buscarCartoesDisponiveisReturn']['formasEnvio']['formasEnvio']:
            formas_envio.append({'codigo': forma['codigo']['#text'], 'descricao': forma['descricao']['#text']})
        
        for c in cartoes:
            print(c)
            if not c.get('liberado',False):
                continue
            soap_envelope = fr'''
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://webservice.econsig.bmg.com">
        <soapenv:Header/>
        <soapenv:Body>
            <web:buscarLimiteSaque soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <param xsi:type="web:DadosCartaoParameter">
                    <login xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{login}</login>
                    <senha xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{senha}</senha>
                    <codigoEntidade xsi:type="xsd:int">{codigo}</codigoEntidade>
                    <cpf xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{cpf}</cpf>
                    <matricula xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{c["matricula"]}</matricula>
                    <numeroContaInterna xsi:type="xsd:long">{c["numero_conta_interna"]}</numeroContaInterna>
                    <tipoSaque xsi:type="xsd:int">{dict_modalidade_saque[c["tipo_saque"]]}</tipoSaque>
                </param>
            </web:buscarLimiteSaque>
        </soapenv:Body>
        </soapenv:Envelope>'''
            
            headers = {
                "Content-Type": "text/xml; charset=utf-8",
                "Content-Length": str(len(soap_envelope)),
                "SOAPAction": "http://webservice.econsig.bmg.com/buscarCartoesDisponiveis",  # Replace with the appropriate SOAP action
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
            }

            response = requests.post(url, data=soap_envelope, headers=headers)
            dict = xmltodict.parse(response.content)
            print('verificar seguro aqui')
            print(dict)
            faultstring = ''
            for elem in root.iter():
                if "faultstring" in elem.tag:
                    faultstring = elem.text
            if 'Ocorreu um erro ao validar o acesso do usuário' in faultstring:
                print('login inválido')
                alert_desenvolvimento(f'LOGIN INVÁLIDO BMG API, {faultstring}')
            elif faultstring:
                print(faultstring)
                try:
                    fault_msg = faultstring.split('ServiceException:')[-1]
                except:
                    fault_msg = faultstring
                alert_desenvolvimento(f'OUTRO ERRO BMG API, {faultstring}')
                continue
            """"""
            envelope = dict.get('soapenv:Envelope', {})
            body = envelope.get('soapenv:Body', {})
            limite_saque_response = body.get('ns1:buscarLimiteSaqueResponse', {})
            limite_saque_return = limite_saque_response.get('buscarLimiteSaqueReturn', {})
            elegivel_comissao = limite_saque_return.get('elegivelComissao', {}).get('#text', 'false')
            elegivel_seguros = limite_saque_return.get('elegivelSeguros', {}).get('#text', 'false')
            excecao_de_regra_de_negocio = limite_saque_return.get('excecaoDeRegraDeNegocio', {}).get('#text', 'false')
            excecao_generica = limite_saque_return.get('excecaoGenerica', {}).get('#text', 'false')
            limite_cartao = limite_saque_return.get('limiteCartao', {}).get('#text', 0)
            limite_disponivel = limite_saque_return.get('limiteDisponivel', {}).get('#text', 0)
            msg_retorno = limite_saque_return.get('mensagemDeErro', {}).get('#text', '')
            permite_abertura_conta_pagamento = limite_saque_return.get('permiteAberturaContaPagamento', {}).get('#text', 'false')
            valor_margem = limite_saque_return.get('valorMargem', {}).get('#text', 0)
            valor_saque_maximo = limite_saque_return.get('valorSaqueMaximo', {}).get('#text', 0)
            valor_saque_minimo = limite_saque_return.get('valorSaqueMinimo', {}).get('#text', 0)
            valor_saque_para_margem_complementar_com_agregacao_de_margem = limite_saque_return.get('valorSaqueParaMargemComplementarComAgregacaoDeMargem', {}).get('#text', 0)
            if 'Cliente não possui limite disponível para saque' in msg_retorno:
                msg_retorno = 'Cliente não possui limite disponível para saque'
            if not msg_retorno:
                msg_retorno = 'Consulta efetuada'
            if 'política interna' in msg_retorno:
                return {'sucesso':False,'msg_retorno':' Cliente com restrição por política interna.','obs':' Cliente com restrição por política interna.'}
            c.update({
                'matricula': matricula,
                "elegivel_comissao":bool(elegivel_comissao.lower() == 'true'),
            "elegivel_seguro": bool(elegivel_seguros.lower() == 'true'),
            "excecao_regra_negocio": excecao_de_regra_de_negocio,
            "excecao_generica": excecao_generica,
            "limite_cartao": limite_cartao,
            "limite_disponivel": round(float(limite_disponivel),2),
            "msg_retorno": msg_retorno,
            "permite_abertura_conta_pagamento": bool(permite_abertura_conta_pagamento.lower() == 'true'),
            "valor_margem": round(float(valor_margem),2),
            "valor_saque_maximo": round(float(valor_saque_maximo),2),
            "valor_saque_minimo": round(float(valor_saque_minimo),2),
            "valor_saque_para_margem_complementar_com_agregacao_de_margem": round(float(valor_saque_para_margem_complementar_com_agregacao_de_margem),2)
        })
            #Nunca passa daqui pois sempre existe msg_retorno
            if msg_retorno:
                print('mensagem_de_erro',msg_retorno)
                continue
            if not elegivel_seguros:
                print('elegivel_seguros',elegivel_seguros)
                continue
            url = 'https://ws1.bmgconsig.com.br/webservices/ProdutoSeguroWebService?wsdl'
            codigo_produto_seguro = 1 if codigo == '1581' else 47
            soap_envelope = rf"""<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://webservice.econsig.bmg.com">
        <soapenv:Header/>
        <soapenv:Body>
            <web:obterPlanosLimiteSaque soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                <param xsi:type="web:PlanosSeguroLimiteSaqueParameter">
                    <login xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{login}</login>
                    <senha xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{senha}</senha>
                    <codigoProdutoSeguro xsi:type="soapenc:int" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{codigo_produto_seguro}</codigoProdutoSeguro>
                    <entidade xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{codigo}</entidade>
                    <matricula xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{matricula}</matricula>
                    <codigoServico xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">106</codigoServico>
                    <numeroInternoConta xsi:type="soapenc:int" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{numero_conta_interna}</numeroInternoConta>
                    <cpf xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">05598799626</cpf>
                </param>
            </web:obterPlanosLimiteSaque>
        </soapenv:Body>
        </soapenv:Envelope>"""
            headers = {
                "Content-Type": "text/xml; charset=utf-8",
                "Content-Length": str(len(soap_envelope)),
                "SOAPAction": "http://webservice.econsig.bmg.com/buscarCartoesDisponiveis",  # Replace with the appropriate SOAP action
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
            }

            response = requests.post(url, data=soap_envelope, headers=headers)
            dict = xmltodict.parse(response.content)
            seguros = []
            plano_limite_saque = dict['soapenv:Envelope']['soapenv:Body']['ns1:obterPlanosLimiteSaqueResponse']['obterPlanosLimiteSaqueReturn']
            if plano_limite_saque.get('mensagemErro',{}).get('#text',''):
                c.update({'seguros':[plano_limite_saque.get('mensagemErro','')]})
                print("plano_limite_saque.get('mensagemErro','')",plano_limite_saque.get('mensagemErro',''))
                continue
            
            planos_com_limite_saque = plano_limite_saque['planosComLimiteSaque']['planosComLimiteSaque']

            for plano in planos_com_limite_saque:
                seguro = {
                    "codigo": plano['codigoPlano']['#text'],
                    "Nome do Plano": plano['nomePlano']['#text'],
                    "Coberturas": []
                }

                coberturas = plano['coberturas']['coberturas']

                for cobertura in coberturas:
                    
                    cobertura_info = cobertura['nomeCobertura']['#text']
                    if  cobertura['valorBeneficio']['#text'] not in ['0.0','0.1']:
                        cobertura_info += ' R$ ' + cobertura['valorBeneficio']['#text']
                    seguro["Coberturas"].append(cobertura_info)
                seguros.append(seguro)
                c.update({'seguros':seguros})
            print(seguros)
    sucesso = False

    for c in cartoes:
        if c.get('valor_saque_maximo') and c.get('valor_saque_maximo') != '0.0':
            sucesso = True
            msg_retorno = 'Consulta Efetuada'
            break
    
    
    # if sucesso:
    #     msg_retorno = 'Saque disponível'
    # else:
    #     if cartoes:
    #         msg_retorno = cartoes[0].get('msg_retorno','consulta falhou')
    #     else:
    #         msg_retorno = 'consulta falhou'
    return {'sucesso':sucesso,'cartoes':cartoes,"cpf":cpf,'msg_retorno':msg_retorno,'obs':msg_retorno}

def login_api_bmg(usuario_id,nome_thread):
    return {'driver':True,'senha_valida':True}

def digitacao_bmg_api(retorno_login,dict_infos):
    simulacao = simular_saque_parcelado_bmg(retorno_login,dict_infos)
    
    url = "https://ws1.bmgconsig.com.br/webservices/SaqueComplementar?wsdl"
    codigo_produto_seguro = 47 if dict_infos["codigo_entidade"] == '4277' else 1
    info_seguro = ''
    if dict_infos['codigo_seguro']:
        info_seguro = f'''<seguros xsi:type="web:ArrayOfSeguro" soapenc:arrayType="web:Seguro[1]">
<seguro>
<tipoSeguro>{codigo_produto_seguro}</tipoSeguro>
<codigoPlano xsi:type="xsd:int">{dict_infos['codigo_seguro']}</codigoPlano>
</seguro>
</seguros>'''
    soap = f'''<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://webservice.econsig.bmg.com" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
   <soapenv:Header/>
   <soapenv:Body>
      <web:gravarPropostaSaqueComplementar soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
         <proposta xsi:type="web:SaqueComplementarParameter">
            <login xsi:type="soapenc:string">{login}</login>
            <senha xsi:type="soapenc:string">{senha}</senha>
            <codigoEntidade xsi:type="xsd:int">{dict_infos["codigo_entidade"]}</codigoEntidade>
            <cpf xsi:type="soapenc:string">{dict_infos["cpf"]}</cpf>
            <matricula xsi:type="soapenc:string">{dict_infos["matricula"]}</matricula>
            <loginConsig xsi:type="soapenc:string">{dict_infos["login_consig"]}</loginConsig>
            <senhaConsig xsi:type="soapenc:string">{dict_infos["senha_consig"]}</senhaConsig>
            <codigoLoja xsi:type="soapenc:int">{dict_infos["codigo_loja"]}</codigoLoja>
            <numeroContaInterna xsi:type="xsd:long">{dict_infos["numero_conta_interna"]}</numeroContaInterna>
            <tipoSaque xsi:type="xsd:int">{dict_infos["tipo_saque"]}</tipoSaque>
            <agencia xsi:type="web:AgenciaParameter">
               <digitoVerificador xsi:type="soapenc:string">{dict_infos["digito_agencia"]}</digitoVerificador>
               <numero xsi:type="soapenc:string">{dict_infos["agencia"]}</numero>
            </agencia>
            <banco xsi:type="web:BancoParameter">
               <numero xsi:type="xsd:int">{dict_infos["codigo_banco"]}</numero>
            </banco>
            <bancoOrdemPagamento xsi:type="xsd:int">{dict_infos["codigo_banco_ordem_pagamento"]}</bancoOrdemPagamento>
            <codigoFormaEnvioTermo xsi:type="soapenc:string">{dict_infos["codigo_forma_envio_termo"]}</codigoFormaEnvioTermo>
            <conta xsi:type="web:ContaParameter">
               <digitoVerificador xsi:type="soapenc:string">{dict_infos["digito_conta"]}</digitoVerificador>
               <numero xsi:type="soapenc:string">{dict_infos["conta"]}</numero>
            </conta>
            <cpfAgente xsi:type="soapenc:string">{dict_infos["cpf_digitador"]}</cpfAgente>
            <finalidadeCredito xsi:type="xsd:int">{dict_infos["codigo_finalidade_credito"]}</finalidadeCredito>
            <formaCredito xsi:type="xsd:int">{dict_infos["codigo_forma_credito"]}</formaCredito>
            <numeroParcelas xsi:type="soapenc:int">{dict_infos["numero_parcelas"]}</numeroParcelas>
            {info_seguro}
            <valorParcela xsi:type="soapenc:double">{dict_infos["valor_parcela"]}</valorParcela>
            <valorSaque xsi:type="soapenc:double">{dict_infos["valor_saque"]}</valorSaque>
            <celular1 xsi:type="web:TelefoneParameter">
               <ddd xsi:type="soapenc:string">{dict_infos["ddd"]}</ddd>
               <numero xsi:type="soapenc:string">{dict_infos["celular"]}</numero>
               <ramal xsi:type="soapenc:string"></ramal>
            </celular1>
         </proposta>
      </web:gravarPropostaSaqueComplementar>
   </soapenv:Body>
</soapenv:Envelope>'''
    
    response = requests.post(url, data=soap)
    print(response.content)
    dict = xmltodict.parse(response.content)
    print(dict)
    if 'soapenv:Fault' in dict['soapenv:Envelope']['soapenv:Body']:
        try:
            msg_erro = dict['soapenv:Envelope']['soapenv:Body']['soapenv:Fault']['faultstring'].split('.ServiceException')[0]
        except:
            msg_erro = dict['soapenv:Envelope']['soapenv:Body']['soapenv:Fault']['faultstring']
        return {'sucesso':False,'msg_retorno':msg_erro,'obs':msg_erro}
    
    return {'sucesso':True,'numero_ade':dict['soapenv:Envelope']['soapenv:Body']['ns1:gravarPropostaSaqueComplementarResponse']['gravarPropostaSaqueComplementarReturn']['#text']}
    #codigo_entidade = 1581 ou 4277
    #tipo_saque = 2 parcelado, 1 saqueautorizado
    #codigo_banco_ordem_pagamento = codigo do banco caso seja op, caso contrário, 0
    #codigo_forma_credito = 2 transf bancária, 18 para conta bmg
    #codigo_finalidade_credito = 1 conta corrente, 2 poupança, 3 conta bmg


def simular_saque_parcelado_bmg(retorno_login,dict_infos):
    url = "https://ws1.bmgconsig.com.br/webservices/SaqueComplementar?wsdl"
    soap = f'''
<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://webservice.econsig.bmg.com">
   <soapenv:Header/>
   <soapenv:Body>
      <web:buscarSimulacao soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
         <param xsi:type="web:SimulacaoCartaoParameter">
            <login xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{login}</login>
            <senha xsi:type="soapenc:string" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">{senha}</senha>
            <codigoEntidade xsi:type="xsd:int">{dict_infos["codigo_entidade"]}</codigoEntidade>
            <valorSaque xsi:type="xsd:double">{dict_infos["valor_saque"]}</valorSaque>
         </param>
      </web:buscarSimulacao>
   </soapenv:Body>
</soapenv:Envelope>'''
    response = requests.post(url, data=soap)
    print(response.content)
    dict = xmltodict.parse(response.content)
    print(dict)
    retorno = dict['soapenv:Envelope']['soapenv:Body']['ns1:buscarSimulacaoResponse']['buscarSimulacaoReturn']['buscarSimulacaoReturn']
    return {'prazo':retorno['numeroParcelas']['#text'],'valor_parcela':retorno['valorParcela']['#text']}

# dict_infos = {
#     "login": "your_login",
#     "senha": "your_password",
#     'login_consig':'SC.56306.07039312964',
#     'senha_consig': 'Consig@2024',
#     "codigo_entidade": "1581",
#     "ddd":'48',
#     'celular':'998316405',
#     "codigo_loja":"56306",
#     "cpf": "39015335249",
#     "matricula": "1367594208",
#     "numero_conta_interna": "8727750",
#     "tipo_saque": "2",
#     "digito_agencia": "0",
#     "agencia": "0001",
#     "codigo_banco": "260",
#     "codigo_banco_ordem_pagamento": "0",
#     "codigo_forma_envio_termo": "15",
#     "digito_conta": "1",
#     "conta": "123456789",
#     "cpf_digitador": "43695106867",
#     "codigo_forma_credito": "2",
#     "numero_parcelas": "84",
#     "valor_parcela": "42.11",
#     "codigo_finalidade_credito":'1',
#     "valor_saque": "1433.00",
#     'codigo_seguro':'76'
# }

def digitacao_bmg(retorno_login, dict_infos):
    login = 'ROBO.56306'
    senha = r'irWY!kQD@6%rb'
    

    soap = f'''<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://webservice.econsig.bmg.com" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
   <soapenv:Header/>
   <soapenv:Body>
      <web:gravarPropostaSaqueComplementar soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
         <proposta xsi:type="web:SaqueComplementarParameter">
            <login xsi:type="soapenc:string">{login}</login>
            <senha xsi:type="soapenc:string">{senha}</senha>
            <codigoEntidade xsi:type="xsd:int">{dict_infos["codigo_entidade"]}</codigoEntidade>
            <cpf xsi:type="soapenc:string">{dict_infos["cpf"]}</cpf>
            <matricula xsi:type="soapenc:string">{dict_infos["matricula"]}</matricula>
            <loginConsig xsi:type="soapenc:string">{dict_infos["login_consig"]}</loginConsig>
            <senhaConsig xsi:type="soapenc:string">{dict_infos["senha_consig"]}</senhaConsig>
            <numeroContaInterna xsi:type="xsd:long">{dict_infos["numero_conta_interna"]}</numeroContaInterna>
            <tipoSaque xsi:type="xsd:int">{dict_infos["tipo_saque"]}</tipoSaque>
            <agencia xsi:type="web:AgenciaParameter">
               <digitoVerificador xsi:type="soapenc:string">{dict_infos["digito_agencia"]}</digitoVerificador>
               <numero xsi:type="soapenc:string">{dict_infos["agencia"]}</numero>
            </agencia>
            <banco xsi:type="web:BancoParameter">
               <numero xsi:type="xsd:int">{dict_infos["codigo_banco"]}</numero>
            </banco>
            <bancoOrdemPagamento xsi:type="xsd:int">{dict_infos["codigo_banco_ordem_pagamento"]}</bancoOrdemPagamento>
            <codigoFormaEnvioTermo xsi:type="soapenc:string">{dict_infos["codigo_forma_envio_termo"]}</codigoFormaEnvioTermo>
            <conta xsi:type="web:ContaParameter">
               <digitoVerificador xsi:type="soapenc:string">{dict_infos["digito_conta"]}</digitoVerificador>
               <numero xsi:type="soapenc:string">{dict_infos["conta"]}</numero>
            </conta>
            <cpfAgente xsi:type="soapenc:string">{dict_infos["cpf_digitador"]}</cpfAgente>
            <finalidadeCredito xsi:type="xsd:int">{dict_infos["codigo_finalidade_credito"]}</finalidadeCredito>
            <formaCredito xsi:type="xsd:int">{dict_infos["codigo_forma_credito"]}</formaCredito>
            <numeroParcelas xsi:type="soapenc:int">{dict_infos["numero_parcelas"]}</numeroParcelas>
            <valorParcela xsi:type="soapenc:double">{dict_infos["valor_parcela"]}</valorParcela>
            <valorSaque xsi:type="soapenc:double">{dict_infos["valor_saque"]}</valorSaque>
         </proposta>
      </web:gravarPropostaSaqueComplementar>
   </soapenv:Body>
</soapenv:Envelope>'''  

  
    url = "https://ws1.bmgconsig.com.br/webservices/SaqueComplementar?wsdl"


    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "Content-Length": str(len(soap)),
        "SOAPAction": "http://webservice.econsig.bmg.com/gravarPropostaSaqueComplementar",  # Replace with the appropriate SOAP action
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

    }

    response = requests.post(url, data=soap, headers=headers)
    print("RESPOSTA:")
    print(response.content)

dict_infos = {
    "cpf": "46128832253",
    "codigo_entidade" : "1581", # 1581 ou 4277
    "matricula": "0474611299",
    "login_consig": "SC.56306.13865437990",
    "senha_consig": "Banco@2025",
    "numero_conta_interna": "4253628",
    "tipo_saque": 2,    #   1-SaqueAutorizado    2-SaqueAutorizadoParcelado    3-SaqueAutorizadoLojista     4-SaqueAutorizadoParceladoLojista     5-SaqueAutorizadoDecimoTerceiro
    "digito_agencia" : 1,
    "agencia" : "0001",
    "codigo_banco" : 260,
    "codigo_banco_ordem_pagamento" : 0, #Informar ‘0’ (zero)caso não seja OP.
    "codigo_forma_envio_termo" : 12, # Balcao(0)    Email(1)    Sedex(2)    GetNet(3)   MotoBoy(4)  EntregaPessoal(5)   CartaoBMGFacilInternet(6)
                                     # CartaoBMGFacilInternetSenhaValidada(7)    DocumentoDigital(8)     Gravacao(9)     InternetBanking(11)     Mobile(12)
    "digito_conta" : 1,
    "conta": 1,
    "cpf_digitador": "43695106867",
    "codigo_finalidade_credito": 2, # 1 - Conta Movimento   2- Conta Poupança
    "codigo_forma_credito": 2, # TedContaSalario(1)    TedContaCredito(2)  OrdemPagamento(3)   AgenciaPagadoraBMG(4)   SemFinanceiro(5)    CartaoBMBCash(6)    
                                # Opcional(7)   BMGCheque(8)   CartaoDinheiroRapido(9)     ChequeAdministrativo(12)    SaqueTecban(14)     SaqueOpAtm(15)
    "numero_parcelas": 84,
    "valor_parcela": 42.11,
    "valor_saque": 1433.00,                            
    
}

retorno_digitacao = digitacao_bmg(True, dict_infos)
print(f"Retorno digitação:{retorno_digitacao}")

# retorno = simular_saque_parcelado_bmg(True,dict_infos)
# retorno_digitacao = digitacao_bmg(True, dict_infos_2)
# print(retorno_digitacao)
# 14581035104
# retorno = consulta_saque_complementar_bmg(True,dict_infos)
# print(retorno)

# retorno = digitacao_bmg_api(True,dict_infos)3
# print(retorno)
# cpfs_df = pd.read_csv('cpfs.csv')
# RETORNOS = {}
# for index,row in cpfs_df.iterrows():
#     cpf = row['CPF']
#     cpf = "".join(re.findall(r"\d+", cpf))
#     cpf = cpf.zfill(11)
#     dict_infos = {'cpf':cpf}
#     retorno = consulta_saque_complementar_bmg(True,dict_infos)
#     if retorno.get('sucesso') and retorno.get('cartoes',[])[0].get('elegivel_seguro'):
#         print(cpf)
#         time.sleep(1000)
#     print('retorno')
#     print(retorno)
#     RETORNOS.update({'cpf':retorno})
# print(RETORNOS)

