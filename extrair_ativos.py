import os
import json
import requests
import time
from datetime import datetime
from utils_meli import renovar_token, buscar_user_id, salvar_jsonl, upload_github

LOCK_FILE = "lock_ativos.txt"
STATUS_FILE = "lock_status.json"

def carregar_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"scroll_id": None, "coletados": 0, "timestamp_inicio": datetime.now().isoformat()}

def salvar_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def remover_arquivos_de_controle():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)

def executar_extracao_ativos():
    if os.path.exists(LOCK_FILE):
        print("🚫 Já em execução. Abortando nova tentativa.")
        return

    with open(LOCK_FILE, "w") as f:
        f.write("locked")

    print(f"🟢 Início da extração em {datetime.now().isoformat()}")

    try:
        status = carregar_status()
        scroll_id = status.get("scroll_id")
        all_ids = []
        coletados_anteriores = status.get("coletados", 0)

        token = renovar_token()
        user_id = buscar_user_id(token)
        headers = {"Authorization": f"Bearer {token}"}
        limit = 100

        print("🚀 Iniciando extração com SCAN + scroll_id...")

        while True:
            params = {
                "status": "active",
                "search_type": "scan",
                "limit": limit
            }
            if scroll_id:
                params["scroll_id"] = scroll_id

            url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                print(f"❌ Erro {response.status_code}: {response.text}")
                break

            data = response.json()
            ids = data.get("results", [])
            scroll_id = data.get("scroll_id")

            if not ids:
                print("✅ Finalizado. Nenhum ID restante.")
                break

            all_ids.extend(ids)
            status["scroll_id"] = scroll_id
            status["coletados"] = coletados_anteriores + len(all_ids)
            salvar_status(status)

            print(f"📦 Coletados até agora: {status['coletados']} anúncios ativos...")
            time.sleep(0.1)

        print(f"🔍 Iniciando detalhamento de {len(all_ids)} anúncios coletados nesta sessão...")
        detalhes = []
        for i, item_id in enumerate(all_ids):
            try:
                r = requests.get(f"https://api.mercadolibre.com/items/{item_id}", headers=headers)
                r.raise_for_status()
                detalhes.append(r.json())
                if i % 50 == 0:
                    print(f"🔍 Detalhado {i}/{len(all_ids)} anúncios.")
                time.sleep(0.2)
            except Exception as e:
                print(f"❌ Erro ao detalhar {item_id}: {e}")

        nome_arquivo = f"ativos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        salvar_jsonl(detalhes, nome_arquivo)
        upload_github(nome_arquivo, nome_arquivo)

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
    finally:
        remover_arquivos_de_controle()
        print(f"✅ Fim da extração em {datetime.now().isoformat()}")
