import requests
import time
import json
from datetime import datetime
from helpers import salvar_dados, salvar_lock_status, carregar_lock_status

ACCESS_TOKEN = "SEU_ACCESS_TOKEN"
SCROLL_URL = "https://api.mercadolibre.com/users/me/search?search_type=scan"
DETAIL_URL_TEMPLATE = "https://api.mercadolibre.com/items?ids={ids}"
LIMITE_TOTAL = 30000


def extrair_anuncios_ativos():
    print(f"🟢 Início da extração em {datetime.now().isoformat()}")
    lock_status = carregar_lock_status()

    if lock_status.get("em_execucao"):
        print("🚫 Já em execução. Abortando nova tentativa.")
        return

    salvar_lock_status(scroll_id=None, total_coletado=0, timestamp=datetime.now().isoformat(), em_execucao=True)

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(SCROLL_URL, headers=headers)
    response.raise_for_status()
    data = response.json()

    scroll_id = data.get("scroll_id")
    results = data.get("results", [])
    anuncios_coletados = []
    coletados = 0

    print("🚀 Iniciando extração com SCAN + scroll_id...")

    while True:
        if not results:
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
                    salvar_dados(anuncios_coletados, "ativos_parciais_completos.json")
                    salvar_lock_status(scroll_id, coletados, datetime.now().isoformat(), em_execucao=False)
                    return

        time.sleep(0.5)
        response = requests.get(f"{SCROLL_URL}&scroll_id={scroll_id}", headers=headers)
        if response.status_code != 200:
            print(f"⚠️ Erro no scroll: {response.text}")
            break

        data = response.json()
        scroll_id = data.get("scroll_id")
        results = data.get("results", [])

    salvar_dados(anuncios_coletados, "ativos_parciais_completos.json")
    salvar_lock_status(scroll_id, coletados, datetime.now().isoformat(), em_execucao=False)
    print(f"✅ Extração finalizada com {coletados} anúncios salvos.")
