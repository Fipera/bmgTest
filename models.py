from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import firebase_admin
from firebase_admin import credentials, firestore, storage
from email.message import EmailMessage
import smtplib
import ssl, sys
from bs4 import BeautifulSoup
import traceback
from datetime import timedelta, datetime,timezone
from selenium.webdriver.common.action_chains import ActionChains
import os, csv, re, json
from selenium import webdriver
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time, tempfile
from selenium.webdriver.support.ui import WebDriverWait
from unidecode import unidecode
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import secrets, hashlib
from random import randint, choice
# import pyautogui
import threading, requests
from google.cloud.firestore_v1.base_query import FieldFilter
import asyncio
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os, zipfile
import os.path
from collections import deque
from requests.auth import HTTPBasicAuth
from twocaptcha import TwoCaptcha
import undetected_chromedriver as uc
from selenium.webdriver.common.proxy import Proxy, ProxyType
import math, psutil
from threading import Lock
from prettytable import PrettyTable
import base64
import urllib,random
import pandas as pd
import urllib3
from google.cloud.firestore_v1 import aggregation

from seleniumbase import Driver
from selenium.common.exceptions import TimeoutException
import platform
import subprocess
# import pyautogui
lock = threading.Lock()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# cpu = 'E6oDLoUeOgCDhChnCBk1''R09mj9pdukL9yztcY9mW'

cpu = os.environ.get("cpu_robo", "note_lucas")
# cpu = 'R09mj9pdukL9yztcY9mW'
# cpu = 'cpu1'
print(cpu)





nome_sistema_bancos = {"626": "c6_bank", "623": "pan"}


def proxies(username, password, endpoint, port, nome):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxies",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (
        endpoint,
        port,
        username,
        password,
    )

    extension = f"{nome}"

    with zipfile.ZipFile(extension, "w") as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return extension



proxy_list = [
    # '200.234.136.191:59100',
    # '200.234.136.79:59100',
    '2.56.249.68:59100'

]


def save_image_to_firestore(image_path, document_name):
    # Open the image file
    print("salvando imagem, ", image_path, document_name)
    with open(image_path, "rb") as image_file:
        # Read the image file
        image_data = image_file.read()

        # Encode image data to base64
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Prepare data to be saved in Firestore
        image_metadata = {
            "image": encoded_image,
            "filename": image_path.split("/")[-1],  # Extract filename
            "mime_type": "image/jpeg",  # Change as per image type
        }

        # Save image data to Firestore
        db.collection("usuarios_banco").document(document_name).update(image_metadata)

def get_chrome_profile_path(profile_name):
    # Definir o caminho base para os perfis do Chrome
    if os.name == 'nt':  # Windows
        base_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')
    elif os.name == 'posix':  # Mac ou Linux
        base_path = os.path.join(os.getenv('HOME'), '.config', 'google-chrome')
    else:
        raise Exception("Sistema operacional não suportado")

    return os.path.join(base_path, profile_name)


def check_profile_exists(usuario_id):

    if os.name == 'nt':  # Windows
        caminho_base = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')
    else:  # Linux
        caminho_base = os.path.expanduser('~/.config/google-chrome')

    # Define o caminho completo do perfil específico do usuário
    caminho_perfil = os.path.join(caminho_base, usuario_id)

    # Verifica se o perfil já existe, se não, ele será criado ao iniciar o driver
    if not os.path.exists(caminho_perfil):
        print(f"Perfil '{usuario_id}' não encontrado. Criando um novo...")
        os.makedirs(caminho_perfil, exist_ok=True)

def kill_chrome_with_profile(profile_path):
    """Mata processos do Chrome que usam o caminho de perfil especificado."""
    try:
        # Itera sobre todos os processos em execução
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'chrome.exe':
                # Verifica se o caminho do perfil está na linha de comando do processo
                if any(profile_path in arg for arg in proc.info['cmdline']):
                    pid = proc.info['pid']
                    print(f"Matando processo com PID: {pid}")
                    proc.kill()  # Mata o processo

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        print(f"Erro ao matar processos: {e}")

def iniciar_driver(profile='', is_mobile=False, uc=True,headless=True,use_proxy=True):
    # Define o caminho base do perfil do Chrome
    caminho_perfil = False
    for n in range(3):
        try:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            print(user_agent)
            options = {
                "uc": uc,
                "headless": headless,
                "is_mobile": is_mobile,
                'agent': user_agent,
                'undetectable':True,
            }

            if os.name == 'nt':  # Windows
                caminho_base = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')
            else:  # Linux
                caminho_base = os.path.expanduser('~/.config/google-chrome')

            # Define o caminho completo do perfil do usuário
            if profile:
                caminho_perfil = os.path.join(caminho_base, profile)

                # Verifica se o perfil já existe, se não, ele será criado
                if not os.path.exists(caminho_perfil):
                    print(f"Perfil '{profile}' não encontrado. Criando um novo...")
                    os.makedirs(caminho_perfil, exist_ok=True)
                options.update({"user_data_dir": caminho_perfil})
                print(f"Usando perfil '{profile}', caminho: {caminho_perfil}")
            if use_proxy:
                print('usando proxy')
                proxy_selected = choice(proxy_list)
                options.update({"proxy": proxy_selected})
            # Configura as opções do Chrome
            
            # Inicializa o driver com as opções configuradas
            print(options)
            if caminho_perfil:
                if kill_chrome_with_profile(caminho_perfil):
                    print('matou chrome')
                    time.sleep(5)
            try:
                driver = Driver(**options)
            
            except:
                # Kill conflicting Chrome processes
                print(f'Falha ao iniciar o driver com perfil {caminho_perfil}, {traceback.format_exc()}')
                kill_chrome_with_profile(caminho_perfil)

                # Retry starting the driver after killing conflicting processes
                try:
                    driver = Driver(**options)
                except Exception as e:
                    print("Falha ao iniciar o driver após fechar processos:")
                    print(traceback.format_exc())
                    return None

            print('iniciou driver')
            driver.maximize_window()
        except:
            print(traceback.format_exc())
            print('falhou')
            continue
        return driver

    else:
        print('falhou 2')
        return False



def create_new_chrome_browser(use_proxy=True, headless=True, profile=False):
    use_proxy = False
    options = Options()
    if profile:
        profile_path = get_chrome_profile_path(profile)
        print(f"Acessando Chrome pelo path '{profile_path}'")
        options.add_argument(f"--user-data-dir={profile_path}")
    if headless:
        options.add_argument("--headless=new")
    ua = UserAgent(os="windows", min_percentage=randint(1, 50))
    user_agent = ua.getChrome
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-agent={user_agent}")
    if use_proxy:

        if len(proxy_list) > 0:
            proxy_selected = choice(proxy_list)
            options.add_argument(f"--proxy-server={proxy_selected}")

    else:
        proxy_selected = []
        pass
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
    except:
        print(traceback.format_exc())

        driver = webdriver.Chrome(
            options=options
        )
        print(traceback.format_exc())
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    while True:
        try:
            driver.get("http://checkip.amazonaws.com//")

            ip = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body"))
            )

            print(ip.text)
            return driver
        except:
            tb = traceback.format_exc()
            print(tb)
            print("proxy falhou")
            alert_desenvolvimento(f'Falha ao acessar proxy {proxy_selected}')
            return create_new_chrome_browser(use_proxy=False,headless=headless,profile=profile)


def create_new_chrome_browser_uc(use_proxy=False, user_agent=False, headless=False,profile=False):
    try:
        options = uc.ChromeOptions()
        print(f'Criando Driver, {use_proxy}, {user_agent}, {headless}, {profile}')
        if use_proxy:
            proxy_selected = choice(proxy_list)
            options.add_argument(
                f'--proxy-server={proxy_selected}'
            )
            # options.add_extension(proxy_selected["name_proxy"])
        if profile:
            profile_path = get_chrome_profile_path(profile)
            print(f"Acessando Chrome pelo path '{profile_path}'")
            options.add_argument(f"--user-data-dir={profile_path}")
        if not user_agent:
            ua = UserAgent(os="windows", min_percentage=randint(1,30))
            user_agent = ua.getChrome
        print("user agent ok")
        print(user_agent)
        options.add_argument(f"--user-agent={user_agent}")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        # Executa o Chrome em modo de teste sem sandboxes (pode ajudar a evitar algumas mensagens)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if headless:
            options.add_argument("--headless")

        try:
            driver = uc.Chrome(
                options=options,
                enable_cdp_events=True,
                headless=headless,
                driver_executable_path="/home/jorge/Desktop/Bots/chromedriver",
                version_main=128,
                use_subprocess=True,
            )
        except:
            print('except open chrome')
            driver = uc.Chrome(
                options=options,
                enable_cdp_events=True,
                headless=headless,
                driver_executable_path='chromedriver.exe',
                use_subprocess=True
            
            )
        driver.get('https://www.google.com')
        time.sleep(5)
        driver.get("https://nowsecure.nl/")
        time.sleep(5)
        print(driver, "driver criado")
        return driver
    except:
        print(traceback.format_exc())

def hash_value(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()


bancos_api_storm = {"inbursa": 152}
tipos_operacao_storm = {
    "margem livre": 1,
    "refinanciamento": 2,
    "cartao sem saque": 5,
    "margem_livre_mais_refinanciamento": 6,
    "cartao_com_saque": 8,
    "refinanciamento_rec": 10,
    "cartao_com_saque_complementar_avista": 14,
    "emprestimo_complementar_inss": 16,
    "portabilidade": 17,
    "portabilidade_mais_refin": 18,
}


def captcha_solver(file_address):

    try:
        solver = TwoCaptcha("08577d94e9e2272e61226ad7f039e3b0")
        id = solver.normal(file=file_address)
        print(id)
        return id.get("code", "0000")
    except:
        tb = traceback.format_exc()
        return "0000"




def format_date(date):
    try:
        date_format = date.strftime("%d/%m/%Y")
    except:
        try:
            date_format = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                "%d/%m/%Y"
            )

        except:
            date_format = ""
    return date_format


def format_hour(date):
    date = date - timedelta(hours=3)
    date_format = date.strftime("%H:%M")

    return date_format


def format_valor(valor):
    try:
        valor = str(valor).replace(",",'_').replace(".", ",").replace("_", ".")
        valor = "R$ {:_.2f}".format(valor)
        return valor
    except:
        return f"R$ {valor}"


def format_date_dd_mm_yyyy_to_yyyy_mm_dd(date_string):
    date_object = datetime.strptime(date_string, "%d/%m/%Y")

    # Convert the date object to the desired format
    formatted_date = date_object.strftime("%Y-%m-%d")

    return formatted_date


def select_element_value(driver, id, value):
    select_element = WebDriverWait(driver, 8).until(
        EC.element_to_be_clickable((By.ID, id))
    )
    select = Select(select_element)
    for n in range(10):
        try:
            select.select_by_value(value)
            break
        except:
            time.sleep(1)
    else:
        pass

# # Credenciais firestore Database
# cred = credentials.Certificate("firebase-sdk.json")
# firebase_app1 = firebase_admin.initialize_app(name="lis1", credential=cred)
# db = firestore.client(app=firebase_app1)
# db_storage = storage.bucket(name="consigbot-3f9ff.appspot.com", app=firebase_app1)
# print("Conectado ao Firestore")
# doc_ref = db.collection('simulador_em_massa').where('user','==','nWkLn0U36xPryfRQZFUD').where('leads_fgts','==',True).get()
# feitas = 0
# for doc in doc_ref:
#     # print(doc.to_dict())
#     linhas_feitas = doc.to_dict().get('linhas_feitas',0)
#     if linhas_feitas > 0:
#         print(f'Achou {linhas_feitas} leads no arquivo {doc.id} na data  {doc.to_dict().get("data")}')
#     feitas = feitas + linhas_feitas
# print(feitas)


def fix_valor(valor):
    if not valor:
        return 0
    try:
        return float(valor)
    except:
        pass
    valor = str(valor).strip()
    
    is_negative = "-" in valor
    
    valor = valor.replace("a.m", "").replace(" .", "")
    try:
        if valor[-3] == "." or valor[-2] == "." or valor[-1] == ".":
            return float(valor) if not is_negative else -float(valor)
        else:
            raise TypeError("not float")
    except:
        padrao = r"R?\s*([\d.,]+)"
        correspondencia = re.search(padrao, valor)
        if correspondencia:
            # Obtemos o grupo correspondente à parte numérica
            valor_numerico = correspondencia.group(1)

            # Substituímos vírgulas por pontos, para garantir que seja um número decimal válido
            while valor[-1] == "0":
                valor = valor[0:-1]
            if len(valor) > 2:
                if valor[-3] == "." or valor[-2] == ".":
                    valor_numerico = valor_numerico.replace(",", "").replace(" ", "")
                if valor[-3] == "," or valor[-2] == "," or valor[-1] == ",":
                    valor_numerico = (
                        valor_numerico.replace(".", "_")
                        .replace(",", ".")
                        .replace("_", "")
                        .replace(" ", "")
                    )
            try:
                result = float(valor_numerico)
                return -result if is_negative else result
            except ValueError:
                if valor == '0,':
                    return 0
                return valor 
        else:
            return valor


def calcular_saldo_devedor(n, p, q0, j):

    saldo_devedor = q0 * (1 + j) ** n - p * (((1 + j) ** n - 1) / j)

    return saldo_devedor


def calcular_valor_emprestimo_inicial(n, p, j):
    q0 = 0  # Valor inicial do empréstimo
    while True:
        q_atual = p * ((1 - (1 + j) ** -n) / j)
        if abs(q_atual - q0) < 0.01:  # Margem de erro
            break
        q0 += 0.01
    return q0


def alert_desenvolvimento(message):
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = f"Alerta ConsigBot"
        msg["From"] = "desenvolvimento@lispromotora.com"
        msg["To"] = "desenvolvimento@lispromotora.com"
        password = "ntxzvsvxnyyayeky"  # minha senha de app
        sender = "desenvolvimento@lispromotora.com"  # meu email
        enviado = send_email(msg, sender, password)
        return enviado
    except:
        print(f'Erro ao enviar email de alerta {message}')
        return False
    


def send_email(msg, sender, password):
    try:
        ctx = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
            server.login(sender, password)
            server.send_message(msg)

        return True
    except Exception as e:
        return False


def verifica_header_df(df, headers):
    for header in headers:
        if header not in df.columns:
            return False
    return True


def set_usuario_banco_invalid(usuario_banco):
    db.collection("usuarios_banco").document(usuario_banco).update(
        {"status": "Senha Inválida", "active": False}
    )


def captcha_solver_google(googlekey, site, version, invisible, enterprise=0):
    api_key = "08577d94e9e2272e61226ad7f039e3b0"
    method = "userrecaptcha"
    # enterprise = 0 or 1
    callback = requests.post(
        f"http://2captcha.com/in.php?key={api_key}&method={method}&googlekey={googlekey}&pageurl={site}&version={version}&invisible={invisible}&enterprise={enterprise}"
    )
    try:
        id = callback.text.split("|")[1]
    except:
        time.sleep(60)
        captcha_solver_google(googlekey, site, version, invisible)
    time.sleep(10)
    for n in range(20):
        try:
            time.sleep(5)
            callback = requests.get(
                f"http://2captcha.com/res.php?key={api_key}&action=get&id={id}"
            )

            if (
                callback.text == "ERROR_WRONG_CAPTCHA_ID"
                or callback.text == "ERROR_CAPTCHA_UNSOLVABLE"
            ):
                callback = requests.post(
                    f"http://2captcha.com/in.php?key={api_key}&method={method}&googlekey={googlekey}&pageurl={site}&version={version}&invisible={invisible}&enterprise={enterprise}"
                )
                try:
                    id = callback.text.split("|")[1]
                except:
                    time.sleep(120)
                    captcha_solver_google(googlekey, site)
                time.sleep(20)
            if callback.text == "CAPCHA_NOT_READY" or "OK|" not in callback.text:
                continue

            break
        except Exception as e:
            time.sleep(5)
    answer = callback.text.split("|")[1]

    return answer


def captcha_solver_cloudfare(siteKey_target, url_target):
    api_key = "08577d94e9e2272e61226ad7f039e3b0"

    solver = TwoCaptcha(api_key)

    try:
        print("resolvendo captcha")
        result = solver.turnstile(
            sitekey= siteKey_target,
            url= url_target,
        )

    except Exception as e:
        return(e)

    else:
        print("Captcha resolvido com sucesso")
        return(result)


def update_counter(last_datetime, last_value):
    date_now = datetime.now().date()
    if last_datetime != date_now:
        return 0
    return last_value + 1


def alert_massa_finalizou(consulta_dict):
    banco = consulta_dict.get("banco")
    user = consulta_dict.get("user")
    email = db.collection("users").document(user).get().to_dict()["email"]
    msg = EmailMessage()
    msg.set_content(
        f"""
Olá!\n
O seu arquivo de consulta em massa no banco {str(banco).title()} finalizou, acesse o consigbot para conferir\n
https://consigbot.com\n\nBoas vendas!\nEquipe Consigbot
                    """
    )
    msg["Subject"] = f"Consigbot - Consulta em massa finalizada"
    msg["From"] = "administrador@consigbot.com"
    msg["To"] = email
    password = "ntxzvsvxnyyayeky"  # minha senha de app
    sender = "desenvolvimento@lispromotora.com"  # meu email
    enviado = send_email(msg, sender, password)
    return enviado



def create_higienizacao_ref(banco, status, tipo):

    higienizacao_ref = (
        db.collection("higienizacao")
        .where(filter=FieldFilter("banco", "==", banco))
        .where(filter=FieldFilter("status", "==", status))
    )

    if tipo:
        higienizacao_ref = higienizacao_ref.where(
            filter=FieldFilter("tipo", "==", tipo)
        )
    if tipo == "consulta_em_massa":
        higienizacao_ref = higienizacao_ref.limit(1)
    return higienizacao_ref.order_by("data", direction=firestore.Query.ASCENDING)


def create_robo(threads_ativos, doc_usuario_banco, usuario_banco, tipo, first_doc):
    dia = datetime.now().day
    for n in range(1, 10000):
        if str(n) in threads_ativos.keys():
            continue
        print(
            "criando novo robo ",
            n,
        )
        if doc_usuario_banco:
            quant_consultas = doc_usuario_banco.get(f"quant_consultas.{str(dia)}", 0)
            quant_consultas_fgts = doc_usuario_banco.get(
                f"quant_consultas_fgts.{str(dia)}", 0
            )
        else:
            quant_consultas = 0
            quant_consultas_fgts = 0
        if first_doc.to_dict().get("id_consulta_massa"):
            db.collection("simulador_em_massa").document(
                first_doc.to_dict().get("id_consulta_massa")
            ).update({"status": "em processamento"})
        threads_ativos[str(n)] = {
            "usuario_logado": usuario_banco,
            "status": "iniciando",
            "doc_consultando": "",
            "docs": [first_doc],
            "ultimo_update": datetime.now(),
            f"quant_consultas": {dia: quant_consultas},
            f"quant_consultas_fgts": {dia: quant_consultas_fgts},
            "segundos_saldo_media": 0,
            "segundos_fgts_media": 0,
            "id_consulta_massa": first_doc.to_dict().get("id_consulta_massa"),
            "tipo": tipo,
            "ativo": False,
            "quantidade_na_fila": 1,
        }
        return


def set_to_updating(doc):
    if doc.to_dict().get("status") == "pendente":
        doc.reference.update({"status": "atualizando"})


def restart_counts(data_robo, banco):
    dia = datetime.now().day
    data_robo.update(
        {
            f"quant_consultas_fgts.{str(dia)}": 0,
            f"quant_consultas.{str(dia)}": 0,
            f"quant_consultas_fgts.{str(dia+1)}": 0,
            f"quant_consultas.{str(dia+1)}": 0,
        }
    )
    doc_users = db.collection("usuarios_banco").where("banco", "==", banco).get()
    batch = db.batch()
    for doc in doc_users:
        batch.update(
            doc.reference,
            {f"quant_consultas_fgts.{str(dia)}": 0, f"quant_consultas.{str(dia)}": 0},
        )
        if len(batch) % 500 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()


# Chame a função para inicializar os usuários disponíveis

# def update_cart(threads_ativos, nome_thread,retorno,doc_infos):


def is_value_in_nested_dicts(value, nested_dict):
    for key, inner_dict in nested_dict.items():
        if isinstance(inner_dict, dict):
            for inner_key, inner_value in inner_dict.items():
                if inner_value == value:
                    return True
    return False


def close_thread(threads_ativos, nome_thread, novo_status="", retorno_login=False):
    id_consulta_massa = threads_ativos.get(nome_thread, {}).get("id_consulta_massa")
    print(f"closing thread {nome_thread}")
    try:
        remove_user_from_robo(threads_ativos, nome_thread, retorno_login)
    except:
        pass
    print(f"thread {nome_thread} finalizada")
    if threads_ativos.get(nome_thread,{}).get('id_consulta_massa'):
        print(f'tem id em massa, {id_consulta_massa}')

        #     filter_1 = FieldFilter("status", "==", 'pendente')
        #     filter_2 = FieldFilter("status", "==", 'atualizando')
        #     doc_hig = db.collection('higienizacao').where('id_consulta_massa','==',threads_ativos.get(nome_thread,{}).get('id_consulta_massa')).where(filter=Or(filters=[filter_1, filter_2])).get()
        #     batch = db.batch()
        #     count = 0
        #     for doc in doc_hig:
        #         new_doc_ref = db.collection('higienizacao').document(doc.id)

        #         batch.update(
        #             new_doc_ref, {'status':'nao liberado','obs':novo_status}
        #         )
        #         count += 1
        #         if count % 500 == 0:
        #             batch.commit()
        #             batch = db.batch()
        #     if count % 500 != 0:
        #         batch.commit()
        if novo_status == 'Sucesso':
            db.collection("logs").add(
                        {
                            "data": firestore.SERVER_TIMESTAMP,
                            "action": "fim_consulta_servidor",
                            'msg':'Consulta em massa Finalizada com Sucesso',
                            "user_name": 'Robô',
                            "usuario_id": 'sistema',
                            'id_consulta_massa':id_consulta_massa
                        }
                    )
            print('atualizando status 1')
            db.collection("simulador_em_massa").document(id_consulta_massa).update({"status": "finalizado", "sub_status": novo_status,'linhas_feitas':threads_ativos[nome_thread].get('linhas_feitas',0)})
        elif novo_status != 'Sucesso' and novo_status:
            db.collection("logs").add(
                        {
                            "data": firestore.SERVER_TIMESTAMP,
                            "action": "fim_consulta_servidor",
                            'msg':f'Consulta em massa Pausada - {novo_status}',
                            "user_name": 'Robô',
                            "usuario_id": 'sistema',
                            'id_consulta_massa':id_consulta_massa
                        }
                    )
            db.collection("simulador_em_massa").document(
            id_consulta_massa
        ).update({"status": "pausado", "sub_status": novo_status,'linhas_feitas':threads_ativos[nome_thread].get('linhas_feitas',0)})
        else:
            db.collection("logs").add(
                        {
                            "data": firestore.SERVER_TIMESTAMP,
                            "action": "fim_consulta_servidor",
                            'msg':f'Consulta em massa Finalizada',
                            "user_name": 'Robô',
                            "usuario_id": 'sistema',
                            'id_consulta_massa':id_consulta_massa
                        }
                    )
            db.collection("simulador_em_massa").document(
                id_consulta_massa
            ).update({"status": "finalizado",'linhas_feitas':threads_ativos[nome_thread].get('linhas_feitas',0)})
    with lock:
        if nome_thread in threads_ativos:
            threads_ativos.pop(nome_thread)
    print(f"thread {nome_thread} finalizado 10")
    return 


def update_usuario_bad_login(threads_ativos, nome_thread, retorno_login):
    user_id = threads_ativos.get(nome_thread,{})["usuario_logado"]
    remove_user_from_robo(threads_ativos, nome_thread, retorno_login)
    try:
        retorno_login["driver"].quit()
    except:
        pass
    if retorno_login["senha_valida"]:
        return
    db.collection("usuarios_banco").document(user_id).update(
        {"status": "Senha Inválida", "data_updated": firestore.SERVER_TIMESTAMP}
    )
    # Incluir pausa nas consultas em massa



def validateCPF(cpf):
    try:
        cpf_numerico = "".join(filter(str.isdigit, cpf))

        # Verificar se tem 11 dígitos
        while len(cpf_numerico) < 11:
            cpf_numerico = "0" + cpf_numerico
        print(cpf_numerico)
        # Verificar se todos os dígitos são iguais
        if cpf_numerico == cpf_numerico[0] * 11:
            return False

        # Calcular os dígitos verificadores
        antigo = [int(d) for d in cpf_numerico]

        # Gera CPF com novos dígitos verificadores e compara com CPF informado
        novo = antigo[:9]
        while len(novo) < 11:
            resto = sum([v * (len(novo) + 1 - i) for i, v in enumerate(novo)]) % 11

            digito_verificador = 0 if resto <= 1 else 11 - resto

            novo.append(digito_verificador)

        if novo == antigo:
            return cpf_numerico

        return False
    except:
        return False
          


def save_to_firebase_cr(dados,doc,cpf):
    print(f'Salvando dados do CR para o CPF {cpf}')
    # Verifica se existe um documento com o CPF do cliente
    if not cpf:
        return

    if not dados.get("erro", False):
        print(f'sem erro')
        if doc.exists:
            print('doc existe')
            telefones = doc.to_dict().get("telefones_list")

            telefones_info = doc.to_dict().get("telefones_info")
            dados.update({"cr_update": firestore.SERVER_TIMESTAMP, "telefones_list": telefones, "telefones_info": telefones_info})
            db.collection("clientes").document(cpf).update(dados)
        else:
            db.collection("clientes").document(cpf).set(dados)
    elif dados.get("erro") == "Não foi encontrado benefício para o CPF informado!":
        if doc.exists:

            db.collection("clientes").document(cpf).update(
                {"cr_update": firestore.SERVER_TIMESTAMP}
            )
        else:
            db.collection("clientes").document(cpf).set({
                'cr_update': firestore.SERVER_TIMESTAMP,
            "cpf": cpf,
            "matriculas": {"FGTS": {"orgao": "fgts"}},
            "cliente": {
                "cpf": cpf,
                "nome": '',
                "nome_mae": '',
                "nome_pai": '',
                "data_nascimento": '',
                "sexo":'',
                "data_source": '',
                "datetime": datetime.now(),
            },
            "dados_bancarios": {},
            "operacoes": [],
            "enderecos": [

            ],
            "documentos": [],
            "telefones_info": [],
            "telefones_list": [],
        }
            )
    else:
        alert_desenvolvimento(f"Erro ao salvar dados do CR para o CPF {cpf},{dados}")

def update_clientes_from_robo(retorno, doc_dict_hig):
    #dict_verification contem a chave correspondente ao valor na base de dados para o valor correspondente ao retorno da consulta

    cpf = doc_dict_hig["cpf"]

    data_source = 5 if doc_dict_hig.get("banco") == "consignado_rapido" else 10
    cpf = "".join(re.findall(r"\d+", cpf))
    cpf = cpf.zfill(11)
    # precisa verificar se cliente existe na db.
    doc = db.collection("clientes").document(cpf).get()
    d_cliente = retorno.get("dados", {})
    print('update robo, ',doc_dict_hig.get("banco"))
    if doc_dict_hig.get("banco") == "consignado_rapido":
        return save_to_firebase_cr(retorno,doc,cpf)
    if not doc.exists:
        doc_dict = {
            "cpf": cpf,
            "matriculas": {"FGTS": {"orgao": "fgts"}},
            "cliente": {
                "cpf": cpf,
                "nome": d_cliente.get("nome_cliente", ""),
                "nome_mae": d_cliente.get("nome_mae", "").lower(),
                "nome_pai": d_cliente.get("nome_pai", "").lower(),
                "data_nascimento": d_cliente.get("data_nascimento", ""),
                "sexo": d_cliente.get("sexo", "").lower(),
                "data_source": data_source,
                "datetime": datetime.now(),
            },
            "dados_bancarios": {},
            "operacoes": [],
            "enderecos": [
                {
                    "uf": d_cliente.get("uf", "").lower(),
                    "cidade": d_cliente.get("cidade", "").lower(),
                    "cep": d_cliente.get("cep", ""),
                    "bairro": d_cliente.get("bairro", ""),
                    "endereco": d_cliente.get("endereco", ""),
                    "numero": d_cliente.get("numero_endereco", ""),
                    "complemento": d_cliente.get("complemento", ""),
                    "datetime": datetime.now(),
                    "data_source": data_source,
                }
            ],
            "documentos": [],
            "telefones_info": [],
            "telefones_list": [],
        }

    else:
        doc_dict = doc.to_dict()
    if "matriculas" not in doc_dict:
        doc_dict["matriculas"] = {"FGTS": {"orgao": "fgts"}}
    if "telefones_list" not in doc_dict:
        doc_dict["telefones_list"] = []
    if "documentos" not in doc_dict:
        doc_dict["documentos"] = []
    if "telefones_info" not in doc_dict:
        doc_dict["telefones_info"] = []
    if "operacoes" not in doc_dict:
        doc_dict["operacoes"] = []
    if "enderecos" not in doc_dict:
        doc_dict["enderecos"] = []
    if "dados_bancarios" not in doc_dict:
        doc_dict["dados_bancarios"] = {}
    if "cliente" not in doc_dict:
        doc_dict["cliente"] = {}

    dict_verification = {
    "bairro": "bairro",
    "data_nascimento": "data_nascimento",
    "email": "email",
    "estado_civil": "estado_civil",
    "nao_perturbe": 'nao_perturbe',
    "nome_cliente": "nome",
    "nome_mae": "nome_mae",
    "nome_pai": "nome_pai",
    "sexo": "sexo",
}


    for key in dict_verification:
        if retorno.get('dados',{}).get(key) and not doc_dict['cliente'].get(dict_verification[key]):
            doc_dict['cliente'][dict_verification[key]] = retorno.get('dados',{}).get(key)
    
    if doc_dict_hig.get("tipo_consulta") == "saldo_devedor":
        operacoes_list = retorno.get("operacoes", [])
        for operacao in operacoes_list:
            matricula = operacao.get('matricula','FGTS')
            chave_matricula = "inss_" + matricula
            if chave_matricula not in doc_dict.get("matriculas", {}):
                doc_dict["matriculas"][chave_matricula] = {
                    "bloqueado_para_emprestimo": "não atualizado",
                    "cpf_representante_legal": "",
                    "data_despacho": "",
                    "data_inicio": "",
                    "data_source": data_source,
                    "datetime": datetime.now(),
                    "eh_pensao_alimenticia": "não atualizado",
                    "especie": "",
                    "grupo_orgao": "inss",
                    "margem_livre": "",
                    "margem_livre_cartao": "",
                    "margem_livre_cartao_beneficio": "",
                    "margem_livre_tipo_4": "",
                    "matricula": matricula,
                    "nit": "",
                    "nome_especie": "",
                    "nome_representante_legal": "",
                    "orgao": "inss",
                    "permite_emprestimo": "não atualizado",
                    "possui_representante_legal": "",
                    "referencia_margem": "",
                    "salario": "",
                    "situacao": "",
                }
            for op in doc_dict.get("operacoes", []):

                if operacao.get("parcela") == op.get("pmt"):
                    op["saldo_devedor"] = operacao.get("saldo_devedor")
                    op["datetime"] = datetime.now()
                    op["em_aberto"] = operacao.get("abertas")
                    op["parcelas"] = operacao.get("prazo_original")
                    op["taxa"] = operacao.get("taxa")
            else:
                doc_dict["operacoes"].append(
                    {
                        "banco": doc_dict_hig.get("banco"),
                        "banco_codigo": next(
                            (
                                chave
                                for chave, valor in nome_sistema_bancos.items()
                                if valor == doc_dict_hig.get("banco")
                            ),
                            0,
                        ),
                        "contrato": operacao.get("contrato", ""),
                        "data_source": 10,
                        "inicio_desconto": operacao.get("inicio_desconto", ""),
                        "data_averbado": operacao.get("data_averbado", ""),
                        "em_aberto": operacao.get("pagas", ""),
                        "fim_desconto": operacao.get("fim_desconto", ""),
                        "parcelas": operacao.get("prazo_original", ""),
                        "pmt": operacao.get("parcela", ""),
                        "saldo_devedor": operacao.get("saldo_devedor", ""),
                        "datetime": datetime.now(),
                        "status": operacao.get("status", "ativo"),
                        "taxa": operacao.get("taxa", ""),
                        "tipo": operacao.get("tipo", "98 - Empréstimo por Consignação"),
                        "valor_emprestimo": operacao.get("valor_original", ""),
                        "obs": operacao.get("obs", ""),
                    }
                )

    if doc_dict_hig.get("tipo_consulta") == "fgts":
        tabelas = retorno.get("tabelas", [])
        maior_valor = 0
        for tabela in tabelas:

            if "FGTS" not in doc_dict.get("matriculas", {}):
                doc_dict["matriculas"]["FGTS"] = {
                    "ultimo_saque": "",
                    "data_source": data_source,
                    "datetime": datetime.now(),
                    "grupo_orgao": "fgts",
                    "orgao": "fgts",
                    "margem_livre": "",
                    "matricula": "fgts",
                    "salario": "",
                    "valor_fgts": "",
                    "situacao": "",
                    'ultimo_update':datetime.now().replace(tzinfo=timezone.utc)
                }
            else:
                doc_dict["matriculas"]["FGTS"]['ultimo_update'] = datetime.now().replace(tzinfo=timezone.utc)
            if tabela.get("liberado", 0) > maior_valor:
                maior_valor = tabela.get("liberado", 0)
            if maior_valor > doc_dict["matriculas"]["FGTS"].get("margem_livre", 0):
                doc_dict["matriculas"]["FGTS"]["margem_livre"] = maior_valor
            doc_dict["matriculas"]["FGTS"]["situacao"] = "ativo"
        if retorno.get("saldo_disponivel_fgts", ""):
            doc_dict["matriculas"]["FGTS"]["valor_fgts"] = retorno.get(
                "saldo_disponivel_fgts", ""
            )
        if "Trabalhador não possui conta de FGTS" in retorno.get("msg_retorno", ""):
            doc_dict["matriculas"]["FGTS"]["situacao"] = "Não possui conta do FGTS"
        if "Mudanças cadastrais na Caixa impedem a contratação" in retorno.get(
            "msg_retorno", ""
        ):
            doc_dict["matriculas"]["FGTS"][
                "situacao"
            ] = "Mudanças cadastrais na Caixa impedem a contratação"
        if "Sem saque aniversario configurado" in retorno.get("msg_retorno",''):
            doc_dict["matriculas"]["FGTS"][
                "situacao"
            ] = "Sem saque aniversario configurado"
        if "Existe uma operação de FGTS em andamento" in retorno.get("msg_retorno",''):
            doc_dict["matriculas"]["FGTS"][
                "situacao"
            ] = "Existe uma operação de FGTS em andamento"

    if doc_dict_hig.get("tipo_consulta",'') == "saque_complementar":
        cartoes_list = retorno.get("cartoes", [])
        for c in cartoes_list:
            matricula = c["matricula"]
            if matricula == '00000000000':
                continue
            chave_matricula = "inss_" + matricula
            if chave_matricula not in doc_dict.get("matriculas", {}):
                doc_dict["matriculas"][chave_matricula] = {
                    "bloqueado_para_emprestimo": "não atualizado",
                    "cpf_representante_legal": "",
                    "data_despacho": "",
                    "data_inicio": "",
                    "data_source": data_source,
                    "datetime": datetime.now(),
                    "eh_pensao_alimenticia": "não atualizado",
                    "especie": "",
                    "grupo_orgao": "inss",
                    "margem_livre": "",
                    "margem_livre_cartao": "",
                    "margem_livre_cartao_beneficio": "",
                    "margem_livre_tipo_4": "",
                    "matricula": matricula,
                    "nit": "",
                    "nome_especie": "",
                    "nome_representante_legal": "",
                    "orgao": "inss",
                    "permite_emprestimo": "não atualizado",
                    "possui_representante_legal": "",
                    "referencia_margem": "",
                    "salario": "",
                    "situacao": "",
                }
            for op in doc_dict.get("operacoes", []):
                if c.get("matricula") == matricula and c.get('tipo_cartao') in op.get('tipo'):
                    op["liberado"] = float(c.get("valor_saque_maximo",0))
                    op["datetime"] = datetime.now()
                    op["msg_retorno"] = c.get("msg_retorno",'')
                    if 'RMC' in op.get('tipo'):
                        doc_dict["matriculas"][chave_matricula]['margem_livre_cartao'] == c.get('valor_parcela',0)
                    else:
                        doc_dict["matriculas"][chave_matricula]['margem_livre_cartao_beneficio'] == c.get('valor_parcela',0)


            else:
                if float(c.get("limite_cartao", 0)) > 0:
                    doc_dict["operacoes"].append(
                        {
                            "banco": doc_dict_hig.get("banco"),
                            "banco_codigo": next(
                                (
                                    chave
                                    for chave, valor in nome_sistema_bancos.items()
                                    if valor == doc_dict_hig.get("banco")
                                ),
                                0,
                            ),
                            "numero_adesao": c.get("numero_adesao", ""),
                            "data_source": 10,
                            "inicio_desconto": c.get("inicio_desconto", ""),
                            "limite_cartao": c.get("limite_cartao", 0),
                            "liberado": c.get("liberado", 0),
                            "matricula": c.get("matricula", ""),
                            "situacao": c.get("situacao", "Ativo"),
                            "tipo": c.get("tipo_cartao", ""),
                            "datetime": datetime.now(),
                            "valor_reservado": c.get("valor_parcela", 0),
                        }
                    )




    if (
        d_cliente.get("celular")
        and "".join(re.findall(r"\d+",str(d_cliente.get("celular", ""))))
        not in doc_dict["telefones_list"]
    ):
        doc_dict["telefones_info"].append(
            {
                "ddd": str(d_cliente.get("ddd_celular", "")),
                "telefone": "".join(re.findall(r"\d+", str(d_cliente.get("celular", "")))),
                "datetime": datetime.now(),
                "data_source": d_cliente.get("data_source", data_source),
                "ranking": d_cliente.get("ranking", 3)
            }
        )
        doc_dict["telefones_list"].append(
            "".join(re.findall(r"\d+",str(d_cliente.get("celular", ""))))
        )
        doc_dict["telefones_info"].sort(key=lambda x: x['ranking'], reverse=True)
    
    # Reordenar telefones_list para corresponder à nova ordem de telefones_info
        ordenacao_indices = [info['telefone'] for info in doc_dict["telefones_info"]]
        doc_dict["telefones_list"] = [telefone for telefone in ordenacao_indices]
    if d_cliente.get("numero_doc") and not any(
        d.get("numero") == d_cliente.get("numero_doc") for d in doc_dict["documentos"]
    ):
        doc_dict["documentos"].append(
            {
                "numero": d_cliente.get("numero_doc", ""),
                "tipo": d_cliente.get("tipo_doc", ""),
                "data_validade": d_cliente.get("data_validade_doc", ""),
                "data_expedicao": d_cliente.get("data_emissao_doc", ""),
                "orgao_expedicao": d_cliente.get("emissor_doc", ""),
                "data_source": data_source,
                "datetime": datetime.now(),
            }
        )



    if doc.exists:
        db.collection("clientes").document(cpf).update(doc_dict)
    else:
        db.collection("clientes").document(cpf).set(doc_dict)
    return


def conferencia_linhas_feitas(threads_ativos,nome_thread):
    try:
        print('conferindo linhas feitas')
        if not threads_ativos.get(nome_thread,{}).get('leads_fgts'):
            return False
        status = 'liberado'

        doc_ref = db.collection('higienizacao').where('status','==',status).where('id_consulta_massa','==',threads_ativos[nome_thread].get('id_consulta_massa'))
        aggregate_query = aggregation.AggregationQuery(doc_ref)
        contagem = aggregate_query.count(alias="all")
        print(contagem)
        results = contagem.get()
        for result in results:
            print(f"Alias of results from query: {result[0].alias}")
            print(f"Number of results from query: {result[0].value}")
        linhas_feitas = result[0].value
        if linhas_feitas >= threads_ativos[nome_thread]['linhas_arquivo']:
            return False
        with lock:
            threads_ativos[nome_thread]['linhas_feitas'] = linhas_feitas
        alert_desenvolvimento(f'Linhas feitas: {linhas_feitas} - Linhas arquivo: {threads_ativos[nome_thread]["linhas_arquivo"]}, thread: {nome_thread}, id_massa: {threads_ativos[nome_thread].get("id_consulta_massa")}')
        db.collection('simulador_em_massa').document(threads_ativos[nome_thread]['id_consulta_massa']).update({'linhas_feitas':linhas_feitas})
        return linhas_feitas
    except:
        return False


def update_base_leads(retorno,original_doc_dict):
    try:
        cpf = "".join(re.findall(r"\d+", original_doc_dict.get('cpf')))
        cpf = cpf.zfill(11)
        if retorno.get('status') == 'na fila' or retorno.get('status') == 'aguardando na fila':
            return
        now = datetime.now(timezone.utc)
        if now.day > 21:
            next_month = now + timedelta(days=30)
            proxima_virada_fgts = next_month.replace(day=21, hour=0, minute=0, second=0, microsecond=0)
        else:
            proxima_virada_fgts = now.replace(day=21, hour=0, minute=0, second=0, microsecond=0)
        doc = db.collection('base_fgts').document(cpf)
        
        if retorno.get('sucesso'):
            target_date = datetime.now(timezone.utc) + timedelta(days=30)
            doc.set({'em_consulta':False,'ultimo_retorno':'liberado','usuarios_utilizaram':firestore.ArrayUnion([original_doc_dict.get('user')]),'data_possivel':target_date,'ultima_higienizacao':now},merge=True)
            return
        if 'não autorizado pelo cliente' in retorno.get('msg_retorno','') or 'impedem a contratação' in retorno.get('msg_retorno',''):
            doc.delete()
            return
        if retorno.get('msg_retorno','') == 'Fora Da Regra Do Banco':
            doc.set({'em_consulta':False,'ultimo_retorno':'saldo insuficiente','data_possivel':proxima_virada_fgts,'ultima_higienizacao':now},merge=True)
            return
        if retorno.get('msg_retorno','') == 'Cliente nao possui saldo FGTS':
            doc.set({'em_consulta':False,'ultimo_retorno':'saldo insuficiente','data_possivel':proxima_virada_fgts,'ultima_higienizacao':now},merge=True)
            return
        if 'Operacao nao permitida antes de' in retorno.get('msg_retorno',''):
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', retorno.get('msg_retorno'))
            if date_match:
                date_str = date_match.group(1)
                target_date = datetime.strptime(date_str, '%d/%m/%Y').replace(tzinfo=timezone.utc) + timedelta(days=1)
            else:
                target_date = proxima_virada_fgts
            doc.set({'em_consulta':False,'ultimo_retorno':'Operacao nao permitida antes de','data_possivel':target_date,'ultima_higienizacao':now},merge=True)
            return
        if retorno.get('msg_retorno') == 'Falha na Consulta':
            doc.set({'em_consulta':False,'ultimo_retorno':'falha na consulta','data_possivel':datetime.now(timezone.utc) + timedelta(days=2),'ultima_higienizacao':now},merge=True)
            return
        doc.set({'em_consulta':False,'ultimo_retorno':'outro retorno','data_possivel':proxima_virada_fgts,'ultima_higienizacao':now},merge=True)
        return
    except:
        db.collection('logs').add({'data':datetime.now(),'retorno':traceback.format_exc()})
        pass


def update_base_leads_saque(retorno,original_doc_dict):
    try:
        cpf = "".join(re.findall(r"\d+", original_doc_dict.get('cpf')))
        cpf = cpf.zfill(11)
        if retorno.get('status') == 'na fila' or retorno.get('status') == 'aguardando na fila':
            return
        now = datetime.now(timezone.utc)
        doc = db.collection('base_saque_complementar').document(cpf)
        
        if retorno.get('sucesso'):
            target_date = datetime.now(timezone.utc) + timedelta(days=180)
            doc.set({'em_consulta':False,'ultimo_retorno':'liberado','usuarios_utilizaram':firestore.ArrayUnion([original_doc_dict.get('user')]),'data_possivel':target_date,'ultima_higienizacao':now},merge=True)
            return
        else:
            if 'política interna' in retorno.get('msg_retorno',''):
                print('política interna, deletado')
                db.collection('logs').add({'action':'delete','retorno':'51845846','data':datetime.now()})
                doc.delete()
                return
            target_date = datetime.now(timezone.utc) + timedelta(days=60)
            doc.set({'em_consulta':False,'ultimo_retorno':'liberado','usuarios_utilizaram':firestore.ArrayUnion([original_doc_dict.get('user')]),'data_possivel':target_date,'ultima_higienizacao':now},merge=True)

            return

    except:
        db.collection('logs').add({'retorno':traceback.format_exc(),'data':datetime.now()})
        print(f'falhou atualizar base saque {traceback.format_exc()}')
        pass






def update_base_leads_assessorare(retorno,original_doc_dict):
    banco = original_doc_dict.get('banco')
    try:
        cpf = "".join(re.findall(r"\d+", original_doc_dict.get('cpf')))
        cpf = cpf.zfill(11)
        if retorno.get('status') == 'consulta na fila' or retorno.get('status') == 'na fila':
            return
        now = datetime.now(timezone.utc)
        if now.day > 21:
            next_month = now + timedelta(days=30)
            proxima_virada_fgts = next_month.replace(day=21, hour=0, minute=0, second=0, microsecond=0)
        else:
            proxima_virada_fgts = now.replace(day=21, hour=0, minute=0, second=0, microsecond=0)
        doc = db.collection('base_fgts_assessorare').document(cpf)
        
        if retorno.get('sucesso'):
            target_date = datetime.now(timezone.utc) - timedelta(days=1)
            doc.set({'higienizado':True,'em_consulta':False,'ultimo_retorno':'liberado','banco':banco,'retorno':retorno,'usuarios_utilizaram':firestore.ArrayUnion([original_doc_dict.get('user')]),'data_possivel':target_date,'ultima_higienizacao':now},merge=True)
            return
        if 'impedem a contratação' in retorno.get('msg_retorno',''):
            doc.delete()
            return
        if 'não autorizado pelo cliente' in retorno.get('msg_retorno',''):
            doc.set({'higienizado':True,'em_consulta':False,'ultimo_retorno':'não autorizado pelo cliente','banco':banco,'retorno':retorno,'data_possivel':datetime.now(timezone.utc) + timedelta(days=9999),'ultima_higienizacao':now},merge=True)
            return
        if retorno.get('msg_retorno','') == 'Fora Da Regra Do Banco':
            doc.set({'higienizado':True,'em_consulta':False,'ultimo_retorno':'saldo insuficiente','data_possivel':proxima_virada_fgts,'ultima_higienizacao':now,'banco':banco,'retorno':retorno},merge=True)
            return
        if retorno.get('msg_retorno','') == 'Cliente nao possui saldo FGTS':
            doc.set({'higienizado':True,'em_consulta':False,'ultimo_retorno':'saldo insuficiente','data_possivel':proxima_virada_fgts,'ultima_higienizacao':now,'banco':banco,'retorno':retorno},merge=True)
            return
        if 'Operacao nao permitida antes de' in retorno.get('msg_retorno',''):
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', retorno.get('msg_retorno'))
            if date_match:
                date_str = date_match.group(1)
                target_date = datetime.strptime(date_str, '%d/%m/%Y').replace(tzinfo=timezone.utc) + timedelta(days=1)
            else:
                target_date = proxima_virada_fgts
            doc.set({'higienizado':True,'em_consulta':False,'ultimo_retorno':'Operacao nao permitida antes de','data_possivel':target_date,'ultima_higienizacao':now,'banco':banco,'retorno':retorno},merge=True)
            return
        if retorno.get('msg_retorno') == 'Falha na Consulta':
            doc.set({'higienizado':True,'em_consulta':False,'ultimo_retorno':'falha na consulta','data_possivel':datetime.now(timezone.utc) + timedelta(days=2),'ultima_higienizacao':now,'banco':banco,'retorno':retorno},merge=True)
            return
        doc.set({'higienizado':True,'em_consulta':False,'ultimo_retorno':'outro retorno','data_possivel':proxima_virada_fgts,'ultima_higienizacao':now,'banco':banco,'retorno':retorno},merge=True)
        return
    except:
        db.collection('logs').add({'action':'erro update base assessorare','retorno':traceback.format_exc()})
        pass

def try_convert(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value
def random_name():
    nomes = [
    "Ana Silva",
    "Pedro Oliveira",
    "Maria Santos",
    "João Souza",
    "Juliana Costa",
    "Lucas Pereira",
    "Carolina Almeida",
    "Gabriel Fernandes",
    "Mariana Carvalho",
    "Rafael Santos",
    "Isabela Lima",
    "Thiago Rocha",
    "Fernanda Gomes",
    "Gustavo Martins",
    "Camila Barbosa",
    "Matheus Araújo",
    "Letícia Cardoso",
    "Bruno Ribeiro",
    "Vanessa Oliveira",
    "Rodrigo Silva",
    "Bianca Castro",
    "André Costa",
    "Larissa Rodrigues",
    "Alexandre Duarte",
    "Amanda Fernandes",
    "Leandro Nunes",
    "Natália Oliveira",
    "Felipe Pereira",
    "Giovanna Sousa",
    "Marcelo Alves",
    "Taís Pereira",
    "Eduardo Santos",
    "Jéssica Lima",
    "Vinícius Castro",
    "Juliana Fernandes",
    "Diego Cardoso",
    "Larissa Santos",
    "Luiz Oliveira",
    "Bruna Costa",
    "Marcos Silva",
    "Renata Sousa",
    "Rafaela Rocha",
    "Daniel Rodrigues",
    "Patrícia Gomes",
    "Lucas Martins",
    "Aline Ribeiro",
    "Gustavo Barbosa",
    "Amanda Silva",
    "Thiago Gonçalves",
    "Letícia Ramos",
    "Caio Carvalho",
    "Fernanda Santos",
    "Douglas Lima",
    "Marina Oliveira",
    "Ricardo Almeida",
    "Fabiana Carvalho",
    "Lucas Fernandes",
    "Renata Barbosa",
    "Guilherme Oliveira",
    "Isabela Santos",
    "Igor Costa",
    "Gabriela Pereira",
    "André Souza",
    "Priscila Lima",
    "Gabriel Fernandes",
    "Mariana Castro",
    "Gustavo Martins",
    "Ana Pereira",
    "Pedro Rocha",
    "Amanda Costa",
    "Leonardo Silva",
    "Bruna Ribeiro",
    "Vinícius Gonçalves",
    "Larissa Alves",
    "Eduardo Carvalho",
    "Camila Oliveira",
    "Rafael Martins",
    "Letícia Rodrigues",
    "Carlos Santos",
    "Gabriela Lima",
    "Marcelo Fernandes",
    "Jéssica Pereira",
    "Felipe Castro",
    "Taís Costa",
    "Douglas Oliveira",
    "Renata Souza",
    "Marcos Almeida",
    "Isabella Silva",
    "Gustavo Oliveira",
    "Juliana Costa",
    "Gabriel Sousa",
    "Bianca Ramos",
    "Bruno Lima",
    "Natália Gonçalves",
    "Lucas Barbosa",
    "Mariana Santos",
    "Rafaela Costa",
    "André Oliveira",
    "Fernanda Silva",
    "Thiago Castro",
]
    return choice(nomes)

def update_retorno_consulta(threads_ativos, nome_thread, retorno, doc, doc_dict):
    print(f'update retorno consulta')
    if retorno.get('tentar_novamente') and threads_ativos[nome_thread].get('tentativas',6) < 5:
        print('tentando novamente')
        return
    # No momento, não considero múltiplas tentativas na contagem
    dia = datetime.now().day
    if retorno.get("status") == "na fila" or retorno.get("status") == "aguardando na fila":
        retorno.update({"status": "na fila"})
    liberado = "liberado" if retorno.get("sucesso", False) else "nao liberado"
    if doc_dict.get('tipo_consulta') != 'digitacao_fgts' and retorno.get('status')!= 'na fila':
        retorno.update({"status": liberado})
    if 'situação_cadastral' in retorno.keys():
        retorno['situacao_cadastral'] = retorno['situação_cadastral']
        retorno.pop('situação_cadastral')
    db.collection("higienizacao").document(doc.id).update(retorno)
    if threads_ativos.get(nome_thread,{}).get("id_consulta_massa") and retorno.get('status') != 'na fila' and retorno.get('status') != 'aguardando na fila' and not threads_ativos.get(nome_thread,{}).get('leads_fgts') and not threads_ativos.get(nome_thread,{}).get('leads_saque'):
        # try:
        #     db.collection("simulador_em_massa").document(
        #         threads_ativos.get(nome_thread,{})["id_consulta_massa"]
        #     ).update({"linhas_feitas": threads_ativos.get(nome_thread,{})['linhas_feitas']})
        # except:
        #     print("nao atualizou linhas feitas")
        with lock:
            threads_ativos.get(nome_thread,{})['linhas_feitas'] += 1
    elif threads_ativos.get(nome_thread,{}).get("id_consulta_massa") and retorno.get('sucesso') and threads_ativos.get(nome_thread,{}).get('leads_fgts'):
        # alert_desenvolvimento(f'Atualizando linhas feitas 2, {retorno}')
        # try:
        #     db.collection("simulador_em_massa").document(
        #         threads_ativos.get(nome_thread,{})["id_consulta_massa"]
        #     ).update({"linhas_feitas": firestore.Increment(1)})
        # except:
        #     print("nao atualizou linhas feitas")
        with lock:
            threads_ativos.get(nome_thread,{})['linhas_feitas'] += 1
    elif threads_ativos.get(nome_thread,{}).get("id_consulta_massa") and retorno.get('sucesso') and threads_ativos.get(nome_thread,{}).get('leads_saque'):
        # alert_desenvolvimento(f'Atualizando linhas feitas 2, {retorno}')
        # try:
        #     db.collection("simulador_em_massa").document(
        #         threads_ativos.get(nome_thread,{})["id_consulta_massa"]
        #     ).update({"linhas_feitas": firestore.Increment(1)})
        # except:
        #     print("nao atualizou linhas feitas")
        with lock:
            threads_ativos.get(nome_thread,{})['linhas_feitas'] += 1

    
    with lock:
        threads_ativos.get(nome_thread,{})["doc_consultando"] = ""
    try:
        if 'dados' in retorno.keys() or doc_dict.get('banco') == 'consignado_rapido':
            print('com dados para atualizar')
            update_clientes_from_robo(retorno, doc_dict)
        else:
            print('sem dados para atualizar')
    except:
        print(traceback.format_exc())
        pass
        #VERIFICAR
    if threads_ativos.get(nome_thread,{}).get('leads_fgts'):
        update_base_leads(retorno,doc_dict)
    if threads_ativos.get(nome_thread,{}).get('user','') in  ["y6T5AJ3mYb1zavW3m4G9",'qkvnF44l2TvoOddJ4HOT']:
        update_base_leads_assessorare(retorno,doc_dict)
    if threads_ativos.get(nome_thread,{}).get('leads_saque'):
        update_base_leads_saque(retorno,doc_dict)
    return


def update_retorno_consulta_in100(threads_ativos, nome_thread, retorno, doc):
    # No momento, não considero múltiplas tentativas na contagem
    dia = datetime.now().day
    if "erro" in retorno:
        liberado = ("nao liberado",)
        obs = retorno["erro"]
        msg_retorno = retorno["erro"]
    else:
        liberado = "liberado"
        obs = "Consulta efetuada"
        msg_retorno = "Consulta efetuada"
    if (
        retorno.get("status") != "finalizado"
    ):  # Aqui para só atualizar propostas que não são digitação nesse formato
        retorno.update({"status": liberado, "obs": obs, "msg_retorno": msg_retorno})
    db.collection("higienizacao").document(doc.id).update(retorno)
    if threads_ativos.get(nome_thread,{})["id_consulta_massa"] != "":
        try:
            db.collection("simulador_em_massa").document(
                threads_ativos.get(nome_thread,{})["id_consulta_massa"]
            ).update({"linhas_feitas": firestore.Increment(1)})
        except:
            print("nao atualizou linhas feitas")
    with lock:
        threads_ativos.get(nome_thread,{})["doc_consultando"] = ""
    return


def quit_driver(driver_retorno):
    try:
        driver_retorno["driver"].quit()
    except:
        print('nao foi possível fechar o driver')
        pass


def remove_user_from_robo(threads_ativos, nome_thread, retorno_login):
    print(f"remove_user_robo, {retorno_login}")
    try:
        retorno_login["driver"].headers = {}

    except:
        pass
    dia = str(datetime.now().day)
    try:
        retorno_login["driver"].quit()
    except:
        pass
    # if nome_thread not in threads_ativos:
    #     return
    # if not threads_ativos.get(nome_thread,{}).get("usuario_logado"):
    #     return
    try:
        doc_usuario_banco = db.collection("usuarios_banco").document(
            threads_ativos.get(nome_thread,{})["usuario_logado"]
        )
        doc_dict = doc_usuario_banco.get().to_dict()
        user = doc_dict["user"]
    except:
        pass

    try:
        doc_usuario_banco.update(
            {
                f"quant_consultas_fgts.{str(dia)}": threads_ativos.get(nome_thread,{})[
                    "quant_consultas_fgts"
                ][dia],
                f"quant_consultas.{str(dia)}": threads_ativos.get(nome_thread,{})[
                    "quant_consultas"
                ][dia],
            }
        )
        db.collection("users").document(user).update(
            {
                f"quant_consultas.{str(dia)}":threads_ativos.get(nome_thread,{})["quant_consultas"][dia],
                f"quant_consultas_fgts.{str(dia)}": 
                    threads_ativos.get(nome_thread,{})["quant_consultas_fgts"][dia]
            }
        )
    except:
        alert_desenvolvimento(
            f"Acréscimo consulta remove_user_from_robo falhou,{traceback.format_exc()}"
        )
    with lock:
        threads_ativos.get(nome_thread,{})["usuario_logado"] = ""
        threads_ativos.get(nome_thread,{})["quant_consultas_agora"] = 0
        threads_ativos.get(nome_thread,{})["deslogar_usuario"] = False



def check_higienizacoes_massa(threads_ativos, banco):
    filter_1 = FieldFilter("status", "==", "em processamento")
    filter_2 = FieldFilter("status", "==", "aguardando na fila")
    filter_4 = FieldFilter("status", "==", "na fila")
    filter_3 = FieldFilter("status", "==", "aguardando")
    # filter_4 = FieldFilter("status", "==", 'atualizando')
    filter_5 = FieldFilter("status", "==", "pendente")
    doc_ref = (
        db.collection("simulador_em_massa")
        .where("banco", "==", banco)
        .where(filter=Or(filters=[filter_1, filter_3]))
        .get()
    )
    for each in doc_ref:
        doc_hig = (
            db.collection("higienizacao")
            .where("id_consulta_massa", "==", each.id)
            .where(filter=Or(filters=[filter_3, filter_2, filter_5,filter_4]))
            .limit(1)
            .get()
        )
        if len(doc_hig) > 0:
            for chave, valor in threads_ativos.items():
                if (
                    "id_consulta_massa" in valor
                    and valor["id_consulta_massa"] == each.id
                ):
                    break
            else:
                if doc_hig[0].to_dict().get("status") != "pendente":
                    doc_hig[0].reference.update({"status": "pendente"})
            continue
        # if not each.to_dict().get('sub_status',False):
        #     alert_massa_finalizou(each.to_dict())
        each.reference.update(
            {
                "status": "finalizado",
                "sub_status": each.to_dict().get("sub_status", "sucesso"),
            }
        )
        check_em_fila = (
            db.collection("simulador_em_massa")
            .where(filter=FieldFilter("status", "==", "aguardando na fila"))
            .where("slot", "==", each.to_dict().get("slot"))
            .order_by("data", direction=firestore.Query.ASCENDING)
            .get()
        )
        if len(check_em_fila) > 0:
            check_em_fila[0].reference.update({"status": "aguardando"})
            doc_hig = (
                db.collection("higienizacao")
                .where("id_consulta_massa", "==", check_em_fila[0].id)
                .limit(1)
                .get()
            )
            doc_hig[0].reference.update({"status": "pendente"})
            # batch = db.batch()
        #     batch.update(
        #         check_em_fila[0], {'status':'pendente'}
        #     )

        #     # Atualize o contador

        #     # Verifique se o limite de 500 documentos por lote foi atingido
        #     if len(batch) % 500 == 0:
        #         # Grave o lote no Firestore
        #         batch.commit()

        #         # Inicialize um novo lote
        #         batch = db.batch()

        # # Grave qualquer documento restante no último lote
        # if len(batch) % 500 != 0:
        #     batch.commit()

def contabilizar_consultas_em_massa(threads_ativos, nome_thread):
    try:
        if not threads_ativos.get(nome_thread,{}).get("id_consulta_massa"):
            return
        filter_1 = FieldFilter("status", "==", 'liberado')
        filter_2 = FieldFilter("status", "==", 'nao liberado')
        if threads_ativos.get(nome_thread,{}).get("leads_fgts") or threads_ativos.get(nome_thread,{}).get("leads_saque"):
            doc_ref = db.collection('higienizacao').where(filter=filter_1).where('id_consulta_massa','==',threads_ativos.get(nome_thread,{}).get("id_consulta_massa"))
        else:
            doc_ref = db.collection('higienizacao').where(filter=Or(filters=[filter_1,filter_2])).where('id_consulta_massa','==',threads_ativos.get(nome_thread,{}).get("id_consulta_massa"))


        aggregate_query = aggregation.AggregationQuery(doc_ref)
        contagem = aggregate_query.count(alias="all")
        print(contagem)
        results = contagem.get()
        for result in results:
            print(f"Alias of results from query: {result[0].alias}")
            print(f"Number of results from query: {result[0].value}")
        linhas_feitas = result[0].value
        db.collection("simulador_em_massa").document(threads_ativos.get(nome_thread,{}).get("id_consulta_massa")).update({"linhas_feitas":linhas_feitas})
        print('contabilizado')
    except:
        print('contagem falhou 2')
        print(traceback.format_exc())
        pass

def disparar_msg_formalizacao(celular,token_connecta, cpf,mensagem):
    try:
        url = 'https://middle-flow.connectacx.com/webhook/mensagem?acao=formalizacao'
        headers = {'Authorization': 'c155ed19c5649631588325542e7c8897'}
        json = {"numero": celular,
        "token": token_connecta,
        "ambiente_connecta": "multichat4.connectacx.com", 
        "mensagem": mensagem}
        try:
            db.collection('base_fgts_assessorare').document(cpf).update({'msg_formalizacao_enviada':datetime.now(timezone.utc)})
        except:
            pass
        retorno = requests.post(url,headers=headers,json=json)
        alert_desenvolvimento(f'Mensagem formalizacao disparada {retorno.content},{cpf}')
        return True
    except:
        alert_desenvolvimento(f'Erro disparar msg formalizacao {traceback.format_exc()},{cpf}')
        return False
# 
# disparar_msg_formalizacao('554891703348','bc02db82b8ec31844f1d3e9f01e3a5dc','00988398451','mensagem correta de formalização')


def import_base_fgts():
    df = pd.read_csv('base3.csv',sep=';',dtype=str)
    batch = db.batch()
    for index,row in df.iterrows():
        cpf = row['CPF']
        if not cpf:
            continue
        cpf = "".join(re.findall(r"\d+", cpf))
        cpf = cpf.zfill(11)
        doc = {
            'cpf': cpf,
            'banco': row['banco'],
            'data_recebido': datetime.now().replace(tzinfo=timezone.utc),
            'data_possivel':datetime.now().replace(tzinfo=timezone.utc),
            'usuarios_utilizaram':[],
            'ultimo_retorno':'nao usado',
            'em_consulta': False
        }    
        # doc_search  = db.collection('higienizacao').where('cpf','==',cpf).where('id_consulta_massa','!=',"").get()
        # for d in doc_search:
        #     if 'não autorizado pelo cliente no APP do FGTS' in d.to_dict().get('msg_retorno',''):
        #         doc = {}
        #         break
        #     if d.to_dict().get('sucesso',''):
        #         doc.update({'ultimo_retorno':'liberado','usuarios_utilizaram':[d.to_dict().get('user','')],
        #                                                         'data_possivel':datetime.now(timezone.utc) + timedelta(days=7)})
        #         break
        #     elif  d.to_dict().get('msg_retorno','') == 'Fora da Regra do Banco':
        #         doc.update({'ultimo_retorno':'saldo insuficiente','data_possivel':datetime.now(timezone.utc) + timedelta(days=7)})
        #         break
        #     elif  d.to_dict().get('msg_retorno','') == 'Cliente nao possui saldo FGTS':
        #         doc.update({'ultimo_retorno':'saldo insuficiente','data_possivel':datetime.now(timezone.utc) + timedelta(days=7)})
        #         break
        # if not doc:
        #     continue
        doc_ref = db.collection('base_fgts').document(cpf)
        batch.set(doc_ref, doc)
        if len(batch) % 500 == 0:
            batch.commit()
    batch.commit()
# import_base_fgts()

# doc_ref = db.collection('base_fgts').where('fonte','==','facta_master').get()
# print(len(doc_ref))
# doc_ref = db.collection('higienizacao').where('tipo_consulta','==','digitacao_fgts').get()
# a = 1
# print(len(doc_ref))
# for doc in doc_ref:
#     print(doc.to_dict())
#     conta = doc.to_dict().get('conta_pagamento')
#     tipo = doc.to_dict().get('tipo_pagamento')
#     banco = doc.to_dict().get('banco_pagamento')
#     agencia = doc.to_dict().get('agencia_pagamento')
#     cpf = doc.to_dict().get('cpf')
#     print(cpf,conta,tipo,banco,agencia)
    
#     a += 1
#     try:
#         doc_cliente = db.collection('base_fgts_assessorare').document(cpf).update({'conta_pagamento':conta,'tipo_pagamento':tipo,'banco_pagamento':banco,'agencia_pagamento':agencia})
#     except:
#         print(traceback.format_exc())
#         pass
    
# print(a)


# # XvninKIA8K7ERpFpEIwi
# 
# # # # filter_2 = FieldFilter("ultimo_retorno", "==", 'saldo insuficiente').where('ultimo_retorno','==','nao usado')
# doc_ref = db.collection('base_fgts_assessorare').where('higienizado','==',True).where('banco','==','facta').where('data_possivel','<=',datetime.now(timezone.utc) + timedelta(days=1)).order_by('data_possivel',firestore.Query.DESCENDING).get()
# print(len(doc_ref))
# for doc in doc_ref:
#     print(doc.to_dict())
    
# print(len(doc_ref))
# cpfs = [doc.id for doc in doc_ref]

# # Criar um DataFrame com os CPFs
# # df = pd.DataFrame(cpfs)

# # # # Salvar o DataFrame em um arquivo CSV
# # df.to_csv("cpfs2.csv", index=False)

# # # Calcular a nova data_possivel
# nova_data_possivel = datetime.now(timezone.utc) - timedelta(days=1)

# # # Atualizar os documentos com a nova data_possivel
# batch = db.batch()
# # for cpf in cpfs:
# #     doc_ref = db.collection('base_fgts').document(cpf)
# #     batch.update(doc_ref,{
# #         'em_consulta': False,
# #         'data_possivel': nova_data_possivel,
# #         'higienizado':True,
# #                 })
# #     if len(batch) >= 499:
# #         print('commit')
# #         batch.commit()
# #         batch = db.batch()

# # batch.commit()
# for cpf in cpfs:
#     doc_ref = db.collection('base_fgts_assessorare').document(cpf)
#     batch.set(doc_ref, {
#         'em_consulta': False,
#         'ultimo_retorno': 'nao usado',
#         'data_possivel': nova_data_possivel,
#         'usuarios_utilizaram': [],
#     })
#     if len(batch) >= 499:
#         batch.commit()
#         batch = db.batch()
# batch.commit()

# print("CSV criado e documentos atualizados com sucesso.")
# doc_ref = db.collection('higienizacao').where('id_consulta_massa','==','PWvOFMOivDnCTWzSZQS0').order_by('data').get()
# nao_ = 0
# sim = 0
# for doc in doc_ref:
#     try:
#         if doc.to_dict().get('status') in['aguardando','atualizando']:
#             print('FALTA')
#             continue
#         print(doc.to_dict())
#         print(doc.to_dict().get('data'))
#         print(doc.to_dict().get('cpf'))
#         print(doc.to_dict().get('obs'))
#         if 'nao autorizado' in doc.to_dict().get('obs'):
#             nao_ += 1
#         if doc.to_dict().get('sucesso'):
#             sim += 1
#     except:
#         print(traceback.format_exc())
#         pass
# print(len(doc_ref))
# print(nao_)
# print(sim)
# #     # Atualize o contador

#     # Verifique se o limite de 500 documentos por lote foi atingido
#     if len(batch) % 500 == 0:
#         # Grave o lote no Firestore
#         batch.commit()

#         # Inicialize um novo lote
#         batch = db.batch()

# # Grave qualquer documento restante no último lote
# if len(batch) % 500 != 0:
#     batch.commit()


# print(datetime.now().weekday())
def get_best_comissao(codigo,valor_liberado):
    data = [
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 60, "comissao": 82.0},
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 75, "comissao": 67.0},
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 100, "comissao": 52.0},
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 60, "comissao": 48.67},
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 125, "comissao": 43.0},
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 60, "comissao": 40.33},
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 75, "comissao": 40.33},
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 150, "comissao": 37.0},
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 75, "comissao": 37.53},
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 100, "comissao": 32.0},
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 200, "comissao": 29.5},
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 125, "comissao": 27.0},
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 100, "comissao": 27.0},
    {"nome": "FGTS - SMART SELECT", "codigo": "53708", "valor": 200, "comissao": 25.0},
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 150, "comissao": 23.67},
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 60, "comissao": 23.67},
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 125, "comissao": 23.0},
    {"nome": "FGTS - GOLD POWER", "codigo": "53678", "valor": 99999, "comissao": 22.0},  # valor not specified
    {"nome": "FGTS - GOLD RN", "codigo": "53236", "valor": 3000, "comissao": 22.0},  # valor adjusted
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 150, "comissao": 20.33},
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 75, "comissao": 20.33},
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 200, "comissao": 19.5},
    {"nome": "FGTS - GOLD SPEED", "codigo": "53686", "valor": 99999, "comissao": 19.0},  # valor not specified
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 200, "comissao": 17.0},
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 100, "comissao": 17.0},
    {"nome": "FGTS - SMART SELECT", "codigo": "53708", "valor": 500, "comissao": 17.0},
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 500, "comissao": 15.0},
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 125, "comissao": 15.0},
    {"nome": "FGTS - GOLD+", "codigo": "53287", "valor": 99999, "comissao": 15.0},  # valor not specified
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 150, "comissao": 13.67},
    {"nome": "FGTS - GOLD PRIME", "codigo": "53694", "valor": 99999, "comissao": 13.0},  # valor not specified
    {"nome": "FGTS - GOLD PLUS+", "codigo": "53201", "valor": 99999, "comissao": 13.0},  # valor not specified
    {"nome": "FGTS - GOLD PLUS", "codigo": "53210", "valor": 99999, "comissao": 12.0},  # valor not specified
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 200, "comissao": 12.0},
    {"nome": "FGTS - GOLD TOP", "codigo": "53228", "valor": 99999, "comissao": 11.0},  # valor not specified
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 500, "comissao": 11.0},
    {"nome": "FGTS - LIGHT", "codigo": "50407", "valor": 99999999, "comissao": 10.0},  # valor not specified
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 500, "comissao": 10.0},
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 500, "comissao": 8.0},
    {"nome": "FGTS - SMART SELECT", "codigo": "53708", "valor": 999999, "comissao": 7.0},
    {"nome": "FGTS - SMART LIGHT", "codigo": "53244", "valor": 999999, "comissao": 5.5},
    {"nome": "FGTS - SMART TURBO", "codigo": "53279", "valor": 999999, "comissao": 5.5},
    {"nome": "FGTS - SMART VIP", "codigo": "53260", "valor": 999999, "comissao": 5.5},
    {"nome": "FGTS - SMART FLEX", "codigo": "53252", "valor": 999999, "comissao": 5.5}
]
    if not valor_liberado:
        return 0
    comissao = 0
    for item in data:
        if str(item['codigo']) != str(codigo):
            continue
        if valor_liberado > item['valor']:
            continue
        comissao_ = round(valor_liberado * (item['comissao'] / 100),2)
        if comissao_ >= comissao:
            comissao = comissao_
    return comissao
def generate_brazilian_cell_number():
    # Lista de DDDs válidos no Brasil (exemplo)
    ddds = [11, 21, 31, 41, 51, 61, 71, 81, 91]

    # Escolhe um DDD aleatório que ainda não foi usado
    ddd = random.choice(ddds)

    # Gera um número de celular aleatório no formato 9XXXX-XXXX
    number = f"9{random.randint(8000, 9999)}{random.randint(1000, 9999)}"

    return ddd, number

codigos_bancos_dict = {
    757: "BANCO KEB HANA DO BRASIL S.A.",
    756: "BANCO COOPERATIVO DO BRASIL S.A. – BANCOOB",
    755: "Bank of America Merrill Lynch Banco Múltiplo S.A.",
    754: "Banco Sistema S.A.",
    753: "Novo Banco Continental S.A. – Banco Múltiplo",
    752: "Banco BNP Paribas Brasil S.A.",
    751: "Scotiabank Brasil S.A. Banco Múltiplo",
    748: "BANCO COOPERATIVO SICREDI S.A.",
    747: "Banco Rabobank International Brasil S.A.",
    746: "Banco Modal S.A.",
    745: "Banco Citibank S.A.",
    743: "Banco Semear S.A.",
    741: "BANCO RIBEIRAO PRETO S.A.",
    739: "Banco Cetelem S.A.",
    712: "Banco Ourinvest S.A.",
    707: "Banco Daycoval S.A.",
    655: "Banco Votorantim S.A.",
    654: "BANCO DIGIMAIS S.A.",
    653: "BANCO INDUSVAL S.A.",
    652: "Itaú Unibanco Holding S.A.",
    643: "Banco Pine S.A.",
    637: "BANCO SOFISA S.A.",
    634: "BANCO TRIANGULO S.A.",
    633: "Banco Rendimento S.A.",
    630: "Banco Smartbank S.A.",
    626: "BANCO C6 CONSIGNADO S.A.",
    623: "Banco Pan S.A.",
    613: "Omni Banco S.A.",
    612: "Banco Guanabara S.A.",
    611: "Banco Paulista S.A.",
    610: "Banco VR S.A.",
    604: "Banco Industrial do Brasil S.A.",
    600: "Banco Luso Brasileiro S.A.",
    545: "SENSO CORRETORA DE CAMBIO E VALORES MOBILIARIOS S.A",
    505: "Banco Credit Suisse (Brasil) S.A.",
    495: "Banco de La Provincia de Buenos Aires",
    492: "ING Bank N.V.",
    488: "JPMorgan Chase Bank, National Association",
    487: "DEUTSCHE BANK S.A. – BANCO ALEMAO",
    479: "Banco ItauBank S.A.",
    477: "Citibank N.A.",
    473: "Banco Caixa Geral – Brasil S.A.",
    464: "Banco Sumitomo Mitsui Brasileiro S.A.",
    456: "Banco MUFG Brasil S.A.",
    422: "Banco Safra S.A.",
    412: "BANCO CAPITAL S.A.",
    408: "BÔNUSCRED SOCIEDADE DE CRÉDITO DIRETO S.A.",
    404: "SUMUP SOCIEDADE DE CRÉDITO DIRETO S.A.",
    403: "CORA SOCIEDADE DE CRÉDITO DIRETO S.A.",
    399: "Kirton Bank S.A. – Banco Múltiplo",
    397: "LISTO SOCIEDADE DE CREDITO DIRETO S.A.",
    396: "HUB PAGAMENTOS S.A",
    394: "Banco Bradesco Financiamentos S.A.",
    393: "Banco Volkswagen S.A.",
    391: "COOPERATIVA DE CREDITO RURAL DE IBIAM – SULCREDI/IBIAM",
    390: "BANCO GM S.A.",
    389: "Banco Mercantil do Brasil S.A.",
    387: "Banco Toyota do Brasil S.A.",
    384: "GLOBAL FINANÇAS SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E À EMPRESA DE PEQUENO",
    383: "BOLETOBANCÁRIO.COM TECNOLOGIA DE PAGAMENTOS LTDA.",
    382: "FIDÚCIA SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E À EMPRESA DE PEQUENO PORTE L",
    381: "BANCO MERCEDES-BENZ DO BRASIL S.A.",
    380: "PICPAY SERVICOS S.A.",
    379: "COOPERFORTE – COOPERATIVA DE ECONOMIA E CRÉDITO MÚTUO DOS FUNCIONÁRIOS DE INSTIT",
    378: "BBC LEASING S.A. – ARRENDAMENTO MERCANTIL",
    377: "MS SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E À EMPRESA DE PEQUENO PORTE LTDA",
    376: "BANCO J.P. MORGAN S.A.",
    374: "REALIZE CRÉDITO, FINANCIAMENTO E INVESTIMENTO S.A.",
    373: "UP.P SOCIEDADE DE EMPRÉSTIMO ENTRE PESSOAS S.A.",
    371: "WARREN CORRETORA DE VALORES MOBILIÁRIOS E CÂMBIO LTDA.",
    370: "Banco Mizuho do Brasil S.A.",
    368: "Banco CSF S.A.",
    367: "VITREO DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS S.A.",
    366: "BANCO SOCIETE GENERALE BRASIL S.A.",
    365: "SOLIDUS S.A. CORRETORA DE CAMBIO E VALORES MOBILIARIOS",
    364: "GERENCIANET S.A.",
    363: "SOCOPA SOCIEDADE CORRETORA PAULISTA S.A.",
    362: "CIELO S.A.",
    360: "TRINUS CAPITAL DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS S.A.",
    359: "ZEMA CRÉDITO, FINANCIAMENTO E INVESTIMENTO S/A",
    355: "ÓTIMO SOCIEDADE DE CRÉDITO DIRETO S.A.",
    354: "NECTON INVESTIMENTOS\xa0 S.A. CORRETORA DE VALORES MOBILIÁRIOS E COMMODITIES",
    352: "TORO CORRETORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA",
    350: "COOPERATIVA DE CRÉDITO RURAL DE PEQUENOS AGRICULTORES E DA REFORMA AGRÁRIA DO CE",
    349: "AL5 S.A. CRÉDITO, FINANCIAMENTO E INVESTIMENTO",
    348: "Banco XP S.A.",
    343: "FFA SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E À EMPRESA DE PEQUENO PORTE LTDA.",
    342: "Creditas Sociedade de Crédito Direto S.A.",
    341: "ITAÚ UNIBANCO S.A.",
    340: "Super Pagamentos e Administração de Meios Eletrônicos S.A.",
    336: "Banco C6 S.A.",
    335: "Banco Digio S.A.",
    332: "Acesso Soluções de Pagamento S.A.",
    331: "Fram Capital Distribuidora de Títulos e Valores Mobiliários S.A.",
    330: "BANCO BARI DE INVESTIMENTOS E FINANCIAMENTOS S.A.",
    329: "QI Sociedade de Crédito Direto S.A.",
    326: "PARATI – CREDITO, FINANCIAMENTO E INVESTIMENTO S.A.",
    325: "Órama Distribuidora de Títulos e Valores Mobiliários S.A.",
    324: "CARTOS SOCIEDADE DE CRÉDITO DIRETO S.A.",
    323: "MERCADOPAGO.COM REPRESENTACOES LTDA.",
    322: "Cooperativa de Crédito Rural de Abelardo Luz – Sulcredi/Crediluz",
    321: "CREFAZ SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E A EMPRESA DE PEQUENO PORTE LT",
    320: "China Construction Bank (Brasil) Banco Múltiplo S/A",
    319: "OM DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA",
    318: "Banco BMG S.A.",
    315: "PI Distribuidora de Títulos e Valores Mobiliários S.A.",
    313: "AMAZÔNIA CORRETORA DE CÂMBIO LTDA.",
    310: "VORTX DISTRIBUIDORA DE TITULOS E VALORES MOBILIARIOS LTDA.",
    309: "CAMBIONET CORRETORA DE CÂMBIO LTDA.",
    307: "Terra Investimentos Distribuidora de Títulos e Valores Mobiliários Ltda.",
    306: "PORTOPAR DISTRIBUIDORA DE TITULOS E VALORES MOBILIARIOS LTDA.",
    301: "BPP Instituição de Pagamento S.A.",
    300: "Banco de la Nacion Argentina",
    299: "SOROCRED\xa0\xa0 CRÉDITO, FINANCIAMENTO E INVESTIMENTO S.A.",
    298: "Vip’s Corretora de Câmbio Ltda.",
    296: "VISION S.A. CORRETORA DE CAMBIO",
    293: "Lastro RDV Distribuidora de Títulos e Valores Mobiliários Ltda.",
    292: "BS2 Distribuidora de Títulos e Valores Mobiliários S.A.",
    290: "Pagseguro Internet S.A.",
    289: "DECYSEO CORRETORA DE CAMBIO LTDA.",
    288: "CAROL DISTRIBUIDORA DE TITULOS E VALORES MOBILIARIOS LTDA.",
    286: "COOPERATIVA DE CRÉDITO RURAL DE OURO\xa0\xa0 SULCREDI/OURO",
    285: "Frente Corretora de Câmbio Ltda.",
    283: "RB CAPITAL INVESTIMENTOS DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LIMITADA",
    281: "Cooperativa de Crédito Rural Coopavel",
    280: "Avista S.A. Crédito, Financiamento e Investimento",
    279: "COOPERATIVA DE CREDITO RURAL DE PRIMAVERA DO LESTE",
    278: "Genial Investimentos Corretora de Valores Mobiliários S.A.",
    276: "Senff S.A. – Crédito, Financiamento e Investimento",
    274: "MONEY PLUS SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E A EMPRESA DE PEQUENO PORT",
    273: "Cooperativa de Crédito Rural de São Miguel do Oeste – Sulcredi/São Miguel",
    272: "AGK CORRETORA DE CAMBIO S.A.",
    271: "IB Corretora de Câmbio, Títulos e Valores Mobiliários S.A.",
    270: "Sagitur Corretora de Câmbio Ltda.",
    269: "BANCO HSBC S.A.",
    268: "BARI COMPANHIA HIPOTECÁRIA",
    266: "BANCO CEDULA S.A.",
    265: "Banco Fator S.A.",
    260: "Nu Pagamentos S.A.",
    259: "MONEYCORP BANCO DE CÂMBIO S.A.",
    254: "PARANÁ BANCO S.A.",
    253: "Bexs Corretora de Câmbio S/A",
    250: "BCV – BANCO DE CRÉDITO E VAREJO S.A.",
    249: "Banco Investcred Unibanco S.A.",
    246: "Banco ABC Brasil S.A.",
    243: "Banco Máxima S.A.",
    241: "BANCO CLASSICO S.A.",
    237: "Banco Bradesco S.A.",
    233: "Banco Cifra S.A.",
    224: "Banco Fibra S.A.",
    222: "BANCO CRÉDIT AGRICOLE BRASIL S.A.",
    218: "Banco BS2 S.A.",
    217: "Banco John Deere S.A.",
    213: "Banco Arbi S.A.",
    212: "Banco Original S.A.",
    208: "Banco BTG Pactual S.A.",
    197: "Stone Pagamentos S.A.",
    196: "FAIR CORRETORA DE CAMBIO S.A.",
    194: "PARMETAL DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA",
    191: "Nova Futura Corretora de Títulos e Valores Mobiliários Ltda.",
    190: "SERVICOOP – COOPERATIVA DE CRÉDITO DOS SERVIDORES PÚBLICOS ESTADUAIS DO RIO GRAN",
    189: "HS FINANCEIRA S/A CREDITO, FINANCIAMENTO E INVESTIMENTOS",
    188: "ATIVA INVESTIMENTOS S.A. CORRETORA DE TÍTULOS, CÂMBIO E VALORES",
    184: "Banco Itaú BBA S.A.",
    183: "SOCRED S.A. – SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E À EMPRESA DE PEQUENO P",
    180: "CM CAPITAL MARKETS CORRETORA DE CÂMBIO, TÍTULOS E VALORES MOBILIÁRIOS LTDA",
    177: "Guide Investimentos S.A. Corretora de Valores",
    174: "PEFISA S.A. – CRÉDITO, FINANCIAMENTO E INVESTIMENTO",
    173: "BRL Trust Distribuidora de Títulos e Valores Mobiliários S.A.",
    169: "BANCO OLÉ CONSIGNADO S.A.",
    163: "Commerzbank Brasil S.A. – Banco Múltiplo",
    159: "Casa do Crédito S.A. Sociedade de Crédito ao Microempreendedor",
    157: "ICAP do Brasil Corretora de Títulos e Valores Mobiliários Ltda.",
    149: "Facta Financeira S.A. – Crédito Financiamento e Investimento",
    146: "GUITTA CORRETORA DE CAMBIO LTDA.",
    145: "LEVYCAM – CORRETORA DE CAMBIO E VALORES LTDA.",
    144: "BEXS BANCO DE CÂMBIO S/A",
    143: "Treviso Corretora de Câmbio S.A.",
    142: "Broker Brasil Corretora de Câmbio Ltda.",
    140: "Easynvest – Título Corretora de Valores SA",
    139: "Intesa Sanpaolo Brasil S.A. – Banco Múltiplo",
    138: "Get Money Corretora de Câmbio S.A.",
    136: "CONFEDERAÇÃO NACIONAL DAS COOPERATIVAS CENTRAIS UNICRED LTDA. – UNICRED DO BRASI",
    134: "BGC LIQUIDEZ DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA",
    133: "CONFEDERAÇÃO NACIONAL DAS COOPERATIVAS CENTRAIS DE CRÉDITO E ECONOMIA FAMILIAR E",
    132: "ICBC do Brasil Banco Múltiplo S.A.",
    131: "TULLETT PREBON BRASIL CORRETORA DE VALORES E CÂMBIO LTDA",
    130: "CARUANA S.A. – SOCIEDADE DE CRÉDITO, FINANCIAMENTO E INVESTIMENTO",
    129: "UBS Brasil Banco de Investimento S.A.",
    128: "MS Bank S.A. Banco de Câmbio",
    127: "Codepe Corretora de Valores e Câmbio S.A.",
    126: "BR Partners Banco de Investimento S.A.",
    125: "Plural S.A. Banco Múltiplo",
    124: "Banco Woori Bank do Brasil S.A.",
    122: "Banco Bradesco BERJ S.A.",
    121: "Banco Agibank S.A.",
    120: "BANCO RODOBENS S.A.",
    119: "Banco Western Union do Brasil S.A.",
    117: "ADVANCED CORRETORA DE CÂMBIO LTDA",
    114: "Central Cooperativa de Crédito no Estado do Espírito Santo – CECOOP",
    113: "Magliano S.A. Corretora de Cambio e Valores Mobiliarios",
    111: "OLIVEIRA TRUST DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIARIOS S.A.",
    108: "PORTOCRED S.A. – CREDITO, FINANCIAMENTO E INVESTIMENTO",
    107: "Banco Bocom BBM S.A.",
    105: "Lecca Crédito, Financiamento e Investimento S/A",
    104: "CAIXA ECONOMICA FEDERAL",
    102: "XP INVESTIMENTOS CORRETORA DE CÂMBIO,TÍTULOS E VALORES MOBILIÁRIOS S/A",
    101: "RENASCENCA DISTRIBUIDORA DE TÍTULOS E VALORES MOBILIÁRIOS LTDA",
    100: "Planner Corretora de Valores S.A.",
    99: "UNIPRIME CENTRAL – CENTRAL INTERESTADUAL DE COOPERATIVAS DE CREDITO LTDA.",
    98: "Credialiança Cooperativa de Crédito Rural",
    97: "Credisis – Central de Cooperativas de Crédito Ltda.",
    96: "Banco B3 S.A.",
    95: "Travelex Banco de Câmbio S.A.",
    94: "Banco Finaxis S.A.",
    93: "PÓLOCRED\xa0\xa0 SOCIEDADE DE CRÉDITO AO MICROEMPREENDEDOR E À EMPRESA DE PEQUENO PORT",
    92: "BRK S.A. Crédito, Financiamento e Investimento",
    91: "CENTRAL DE COOPERATIVAS DE ECONOMIA E CRÉDITO MÚTUO DO ESTADO DO RIO GRANDE DO S",
    89: "CREDISAN COOPERATIVA DE CRÉDITO",
    88: "BANCO RANDON S.A.",
    85: "Cooperativa Central de Crédito – Ailos",
    84: "UNIPRIME NORTE DO PARANÁ – COOPERATIVA DE CRÉDITO LTDA",
    83: "Banco da China Brasil S.A.",
    82: "BANCO TOPÁZIO S.A.",
    81: "BancoSeguro S.A.",
    80: "B&T CORRETORA DE CAMBIO LTDA.",
    79: "Banco Original do Agronegócio S.A.",
    78: "Haitong Banco de Investimento do Brasil S.A.",
    77: "Banco Inter S.A.",
    76: "Banco KDB do Brasil S.A.",
    75: "Banco ABN Amro S.A.",
    74: "Banco J. Safra S.A.",
    70: "BRB – BANCO DE BRASILIA S.A.",
    69: "Banco Crefisa S.A.",
    66: "BANCO MORGAN STANLEY S.A.",
    65: "Banco AndBank (Brasil) S.A.",
    64: "GOLDMAN SACHS DO BRASIL BANCO MULTIPLO S.A.",
    63: "Banco Bradescard S.A.",
    62: "Hipercard Banco Múltiplo S.A.",
    60: "Confidence Corretora de Câmbio S.A.",
    47: "Banco do Estado de Sergipe S.A.",
    41: "Banco do Estado do Rio Grande do Sul S.A.",
    40: "Banco Cargill S.A.",
    37: "Banco do Estado do Pará S.A.",
    36: "Banco Bradesco BBI S.A.",
    33: "BANCO SANTANDER (BRASIL) S.A.",
    29: "Banco Itaú Consignado S.A.",
    25: "Banco Alfa S.A.",
    24: "Banco Bandepe S.A.",
    21: "BANESTES S.A. BANCO DO ESTADO DO ESPIRITO SANTO",
    18: "Banco Tricury S.A.",
    17: "BNY Mellon Banco S.A.",
    16: "COOPERATIVA DE CRÉDITO MÚTUO DOS DESPACHANTES DE TRÂNSITO DE SANTA CATARINA E RI",
    15: "UBS Brasil Corretora de Câmbio, Títulos e Valores Mobiliários S.A.",
    14: "STATE STREET BRASIL S.A. ? BANCO COMERCIAL",
    12: "Banco Inbursa S.A.",
    11: "CREDIT SUISSE HEDGING-GRIFFO CORRETORA DE VALORES S.A",
    10: "CREDICOAMO CREDITO RURAL COOPERATIVA",
    7: "BANCO NACIONAL DE DESENVOLVIMENTO ECONOMICO E SOCIAL",
    4: "Banco do Nordeste do Brasil S.A.",
    3: "BANCO DA AMAZONIA S.A.",
    1: "Banco do Brasil S.A.",
}
codigo_beneficios_inss_dict = {
    7: "Aposentadoria por idade do trabalhador rural",
    8: "Aposentadoria por idade do empregador rural",
    41: "Aposentadoria por idade",
    52: "Aposentadoria por idade (Extinto Plano Básico)",
    78: "Aposentadoria por idade de ex-combatente marítimo (Lei nº 1.756/52)",
    81: "Aposentadoria por idade compulsória (Ex-SASSE)",
    4: "Aposentadoria por invalidez do trabalhador rural",
    6: "Aposentadoria por invalidez do empregador rural",
    32: "Aposentadoria por invalidez previdenciária",
    33: "Aposentadoria por invalidez de aeronauta",
    34: "Aposentadoria por invalidez de ex-combatente marítimo (Lei nº 1.756/52)",
    51: "Aposentadoria por invalidez (Extinto Plano Básico)",
    83: "Aposentadoria por invalidez (Ex-SASSE)",
    42: "Aposentadoria por tempo de contribuição previdenciária",
    43: "Aposentadoria por tempo de contribuição de ex-combatente",
    44: "Aposentadoria por tempo de contribuição de aeronauta",
    45: "Aposentadoria por tempo de contribuição de jornalista profissional",
    46: "Aposentadoria por tempo de contribuição especial",
    49: "Aposentadoria por tempo de contribuição ordinária",
    57: "Aposentadoria por tempo de contribuição de professor (Emenda Const.18/81)",
    72: "Apos. por tempo de contribuição de ex-combatente marítimo (Lei 1.756/52)",
    82: "Aposentadoria por tempo de contribuição (Ex-SASSE)",
    1: "Pensão por morte do trabalhador rural",
    3: "Pensão por morte do empregador rural",
    21: "Pensão por morte previdenciária",
    23: "Pensão por morte de ex-combatente",
    27: "Pensão por morte de servidor público federal com dupla aposentadoria",
    28: "Pensão por morte do Regime Geral (Decreto nº 20.465/31)",
    29: "Pensão por morte de ex-combatente marítimo (Lei nº 1.756/52)",
    55: "Pensão por morte (Extinto Plano Básico)",
    84: "Pensão por morte (Ex-SASSE)",
    13: "Auxílio-doença do trabalhador rural",
    15: "Auxílio-reclusão do trabalhador rural",
    25: "Auxílio-reclusão",
    31: "Auxílio-doença previdenciário",
    36: "Auxílio Acidente",
    50: "Auxílio-doença\xa0 (Extinto Plano Básico)",
    2: "Pensão por morte por acidente do trabalho do trabalhador rural",
    5: "Aposentadoria por invalidez por acidente do trabalho do trabalhador Rural",
    10: "Auxílio-doença por acidente do trabalho do trabalhador rural",
    91: "Auxílio-doença por acidente do trabalho",
    92: "Aposentadoria por invalidez por acidente do trabalho",
    93: "Pensão por morte por acidente do trabalho",
    94: "Auxílio-acidente por acidente do trabalho",
    95: "Auxílio-suplementar por acidente do trabalho",
    11: "Renda mensal vitalícia por invalidez do trabalhador rural (Lei nº 6.179/74)",
    12: "Renda mensal vitalícia por idade do trabalhador rural (Lei nº 6.179/74)",
    30: "Renda mensal vitalícia por invalidez (Lei nº 6179/74)",
    40: "Renda mensal vitalícia por idade (Lei nº 6.179/74)",
    85: "Pensão mensal vitalícia do seringueiro (Lei nº 7.986/89)",
    86: "Pensão mensal vitalícia do dep.do seringueiro (Lei nº 7.986/89)",
    87: "Amparo assistencial ao portador de deficiência (LOAS)",
    88: "Amparo assistencial ao idoso (LOAS)",
    47: "Abono de permanência em serviço 25%",
    48: "Abono de permanência em serviço 20%",
    68: "Pecúlio especial de aposentadoria",
    79: "Abono de servidor aposentado pela autarquia empr.(Lei 1.756/52)",
    80: "Salário-maternidade",
    22: "Pensão por morte estatutária",
    26: "Pensão Especial (Lei nº 593/48)",
    37: "Aposentadoria de extranumerário da União",
    38: "Aposentadoria da extinta CAPIN",
    54: "Pensão especial vitalícia (Lei nº 9.793/99)",
    56: "Pensão mensal vitalícia por síndrome de talidomida (Lei nº 7.070/82)",
    58: "Aposentadoria excepcional do anistiado (Lei nº 6.683/79)",
    59: "Pensão por morte excepcional do anistiado (Lei nº 6.683/79)",
    60: "Pensão especial mensal vitalícia (Lei 10.923, de 24/07/2004)",
    76: "Salário-família estatutário da RFFSA (Decreto-lei nº 956/69)",
    89: "Pensão especial aos depedentes de vítimas fatais p/ contaminação na hemodiálise",
    96: "Pensão especial às pessoas atingidas pela hanseníase (Lei nº 11.520/2007)",
}
