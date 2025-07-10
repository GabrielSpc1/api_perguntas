import requests
import random
import datetime
from dateutil import parser
import logging
import time

# === CONFIGURAÇÃO DO LOG ===
logging.basicConfig(
    filename="log_respostas.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

# === CONFIGURAÇÕES ===
CLIENT_ID = '6439275970401699'
CLIENT_SECRET = 'Pw9VVyEx4Wj3iYSeNFVvCWSd44I1j7hZ'
REFRESH_TOKEN = 'TG-685eefa4befee4000139f1cc-162089212'
LIMITE_PERGUNTAS = 10

respostas_automaticas = [
    "Olá, tudo bem? Qual o modelo do seu carro e o ano? Precisa de mais alguma peça?",
    "Boa tarde! Poderia informar o ano e modelo do seu carro? Está procurando mais peças também?",
    "Olá! Me diga por favor o modelo e ano do veículo. Posso ajudar com outras peças também?",
    "Oi! Qual o modelo e o ano do seu carro? Precisa de mais alguma coisa além disso?",
    "Se possível, envie o ano e modelo do carro. Tem interesse em mais peças?",
    "Olá! Qual o ano e modelo do seu carro? Estou à disposição para mais peças também.",
    "Bom dia! Me diga o modelo e o ano do carro. Procurando mais alguma peça?",
    "Oi! Qual o ano do seu carro e modelo? Se precisar de mais peças, posso ajudar.",
    "Olá, informe o modelo e ano do veículo. Está atrás de mais alguma peça?",
    "Me diga o modelo e ano do carro. Aproveito para verificar outras peças que precise."
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

def buscar_perguntas_na_faixa(token):
    headers = {"Authorization": f"Bearer {token}"}
    user_id = requests.get("https://api.mercadolibre.com/users/me", headers=headers).json()['id']
    url = f"https://api.mercadolibre.com/questions/search?seller_id={user_id}&status=UNANSWERED&limit={LIMITE_PERGUNTAS}"
    perguntas = requests.get(url, headers=headers).json().get("questions", [])

    perguntas_filtradas = []

    for p in perguntas:
        hora_brasilia = parser.isoparse(p['date_created']).astimezone().hour
        from_id = p['from']['id']
        item_id = p['item_id']
        pergunta_id = p['id']

        historico_url = f"https://api.mercadolibre.com/questions/search?item={item_id}"
        historico = requests.get(historico_url, headers=headers).json().get("questions", [])
        ja_perguntou = any(q['from']['id'] == from_id and q['id'] != pergunta_id for q in historico)

        if ja_perguntou:
            logging.info(f"⏭ Pulando pergunta duplicada do usuário {from_id} no item {item_id}")
            continue

        if 13 <= hora_brasilia < 19:
            perguntas_filtradas.append(p)

    return perguntas_filtradas

def enviar_resposta(token, pergunta_id, texto):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"question_id": pergunta_id, "text": texto}
    r = requests.post("https://api.mercadolibre.com/answers", headers=headers, json=payload)
    return r.status_code, r.text

# === LOOP CONTÍNUO ===
if __name__ == "__main__":
    logging.info("🚀 Iniciando monitoramento contínuo de perguntas...")
    while True:
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

        time.sleep(300)  # Espera 5 minutos antes da próxima execução
