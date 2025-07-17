import time
import json
from datetime import datetime
from helpers import salvar_dados, salvar_lock_status, carregar_lock_status
from utils_meli import renovar_token, buscar_user_id
import requests

BASE_URL = "https://api.mercadolibre.com/users/{user_id}/items/search"
DETAIL_URL_TEMPLATE = "https://api.mercadolibre.com/items?ids={ids}"
LIMITE_TOTAL = 30000
PAGINA_LIMITE = 50

def extrair_anuncios_ativos():
    print(f"🟢 Início da extração em {datetime.now().isoformat()}")

    lock_status = carregar_lock_status()
    if lock_status.get("em_execucao"):
        print("🚫 Já em execução. Abortando nova tentativa.")
        return

    salvar_lock_status(scroll_id=None, total_coletado=0, timestamp=datetime.now().isoformat(), em_execucao=True)

    print("🔄 Renovando token...")
    access_token = renovar_token()
    print(f"✅ Token obtido: {access_token[:10]}...")

    try:
        print("🔍 Buscando user_id...")
        user_id = buscar_user_id(access_token)
        print(f"✅ user_id: {user_id}")
    except Exception as e:
        print(f"❌ Erro ao buscar user_id: {str(e)}")
        salvar_lock_status(None, 0, datetime.now().isoformat(), em_execucao=False)
        return

    offset = 0
    coletados = 0
    anuncios_coletados = []

    print("🚀 Iniciando extração com paginação segura...")

    while coletados < LIMITE_TOTAL:
        url = f"{BASE_URL.format(user_id=user_id)}?status=active&offset={offset}&limit={PAGINA_LIMITE}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"⚠️ Erro ao buscar página: {resp.text}")
            break

        results = resp.json().get("results", [])
        if not results:
            print("✅ Nenhum resultado adicional. Fim da extração.")
            break

        ids_lote = ",".join(results)
        detalhes_url = DETAIL_URL_TEMPLATE.format(ids=ids_lote)
        detalhes_resp = requests.get(detalhes_url, headers=headers)
        if detalhes_resp.status_code != 200:
            print(f"⚠️ Erro ao buscar detalhes: {detalhes_resp.text}")
            break

        detalhes = detalhes_resp.json()
        for item in detalhes:
            anuncio_detalhado = item.get("body", {})
            if anuncio_detalhado:
                anuncios_coletados.append(anuncio_detalhado)
                coletados += 1

                if coletados % 100 == 0:
                    print(f"📦 Coletados até agora: {coletados} anúncios ativos...")

                if coletados >= LIMITE_TOTAL:
                    print(f"🚫 Limite de {LIMITE_TOTAL} atingido. Encerrando extração.")
                    break

        offset += PAGINA_LIMITE
        time.sleep(0.5)

    salvar_dados(anuncios_coletados, "ativos_parciais_completos.json")
    salvar_lock_status(None, coletados, datetime.now().isoformat(), em_execucao=False)
    print(f"✅ Extração finalizada com {coletados} anúncios salvos.")


def executar_extracao_ativos():
    extrair_anuncios_ativos()
