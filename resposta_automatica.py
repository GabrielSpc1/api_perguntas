import os
import requests
import random
import datetime
from dateutil import parser
import logging
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# === CARREGAR VARIÁVEIS DE AMBIENTE ===
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
LIMITE_PERGUNTAS = 10

# === CONFIGURAÇÃO DO LOG VIA STDOUT ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

# === RESPOSTAS PADRÃO ===
respostas_automaticas = [
    "Olá, tudo bem? Qual o modelo do seu carro e o ano? Precisa de mais alguma peça? Att Assistente Sportcar",
    "Olá, como está?! Poderia informar o ano e modelo do seu carro? Está procurando mais peças também? Att Assistente Sportcar",
    "Olá! Me diga por favor o modelo e ano do veículo. Posso ajudar com outras peças também? Att Assistente Sportcar",
    "Olá, como vai? Qual o modelo e o ano do seu carro? Precisa de mais alguma coisa além disso? Att Assistente Sportcar",
    "Se possível, envie o ano e modelo do carro. Tem interesse em mais peças? Att Assistente Sportcar",
    "Olá! Qual o ano e modelo do seu carro? Estou à disposição para mais peças também. Att Assistente Sportcar",
    "Olá, tudo bem? Me diga o modelo e o ano do carro. Procurando mais alguma peça? Att Assistente Sportcar",
    "Oi! Qual o ano do seu carro e modelo? Se precisar de mais peças, posso ajudar. Att Assistente Sportcar",
    "Olá, informe o modelo e ano do veículo. Está atrás de mais alguma peça? Att Assistente Sportcar",
    "Me diga o modelo e ano do carro. Aproveito para verificar outras peças que precise. Att Assistente Sportcar"
]

def obter_access_token():
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }
    r = requests.post(url, data=payload)
    r.raise_for_status()
    return r.json()['access_token']

def horario_permitido(hora_brasilia, dia_semana):
    if dia_semana < 5:  # Dias úteis
        return 17 <= hora_brasilia <= 23
    else:  # Sábado e domingo
        return True

def buscar_perguntas_na_faixa(token):
    headers = {"Authorization": f"Bearer {token}"}
    user_id = requests.get("https://api.mercadolibre.com/users/me", headers=headers).json()['id']
    url = f"https://api.mercadolibre.com/questions/search?seller_id={user_id}&status=UNANSWERED&limit={LIMITE_PERGUNTAS}"
    perguntas = requests.get(url, headers=headers).json().get("questions", [])

    perguntas_filtradas = []

    for p in perguntas:
        data_criacao = parser.isoparse(p['date_created']).astimezone(ZoneInfo("America/Sao_Paulo"))
        hora_brasilia = data_criacao.hour
        dia_semana = data_criacao.weekday()  # 0 = segunda, 6 = domingo

        logging.info(f"🕒 Verificando horário da pergunta: {hora_brasilia}h (dia {dia_semana})")

        from_id = p['from']['id']
        item_id = p['item_id']
        pergunta_id = p['id']

        historico_url = f"https://api.mercadolibre.com/questions/search?item={item_id}"
        historico = requests.get(historico_url, headers=headers).json().get("questions", [])
        ja_perguntou = any(q['from']['id'] == from_id and q['id'] != pergunta_id for q in historico)

        if ja_perguntou:
            logging.info(f"⏭ Pulando pergunta duplicada do usuário {from_id} no item {item_id}")
            continue

        if horario_permitido(hora_brasilia, dia_semana):
            perguntas_filtradas.append(p)

    return perguntas_filtradas

def enviar_resposta(token, pergunta_id, texto):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"question_id": pergunta_id, "text": texto}
    r = requests.post("https://api.mercadolibre.com/answers", headers=headers, json=payload)
    return r.status_code, r.text

# === EXECUÇÃO ÚNICA ===
def main():
    logging.info("🚀 Iniciando execução única de perguntas...")
    try:
        token = obter_access_token()
        perguntas = buscar_perguntas_na_faixa(token)

        if not perguntas:
            logging.info("Nenhuma pergunta nova encontrada no horário permitido.")
        else:
            for p in perguntas:
                pergunta_id = p['id']
                texto_pergunta = p['text']
                item_id = p['item_id']
                comprador_id = p['from']['id']

                titulo = requests.get(f"https://api.mercadolibre.com/items/{item_id}").json().get('title', 'Sem título')
                resposta = random.choice(respostas_automaticas)

                logging.info(f"📦 Produto: {titulo}")
                logging.info(f"❓ Pergunta: {texto_pergunta} (de {comprador_id})")
                logging.info(f"💬 Resposta gerada: {resposta}")

                status, retorno = enviar_resposta(token, pergunta_id, resposta)
                if status in [200, 201]:
                    logging.info(f"✅ Resposta enviada com sucesso para pergunta {pergunta_id}")
                else:
                    logging.error(f"❌ Erro ao enviar resposta {pergunta_id}: {status} - {retorno}")

    except Exception as e:
        logging.exception("❌ Erro inesperado durante execução do script")

if __name__ == "__main__":
    main()
