import os
import json
import time
from datetime import datetime
import requests
from utils_meli import renovar_token, buscar_user_id, salvar_jsonl, upload_github

def executar_extracao_ativos():
    # Carrega estado anterior (se existir)
    estado_path = "lock_status.json"
    estado = {}
    if os.path.exists(estado_path):
        with open(estado_path, "r") as f:
            estado = json.load(f)
        if estado.get("em_execucao"):
            print("🚫 Já em execução. Abortando nova tentativa.")
            return

    # Atualiza estado para em execução
    estado = {
        "em_execucao": True,
        "scroll_id": estado.get("scroll_id"),
        "coletados": estado.get("coletados", 0),
        "timestamp_inicio": datetime.now().isoformat()
    }
    with open(estado_path, "w") as f:
        json.dump(estado, f)

    print(f"🟢 Início da extração em {estado['timestamp_inicio']}")

    try:
        token = renovar_token()
        user_id = buscar_user_id(token)
        headers = {"Authorization": f"Bearer {token}"}

        limit = 100
        scroll_id = estado.get("scroll_id")
        coletados = estado.get("coletados", 0)
        all_ids = []

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
                break

            all_ids.extend(ids)
            coletados += len(ids)

            print(f"📦 Coletados até agora: {coletados} anúncios ativos...")

            # Atualiza checkpoint a cada 10.000
            if coletados % 10000 < limit:
                estado.update({
                    "scroll_id": scroll_id,
                    "coletados": coletados,
                    "timestamp_checkpoint": datetime.now().isoformat()
                })
                with open(estado_path, "w") as f:
                    json.dump(estado, f)

            time.sleep(0.1)

        print(f"✅ Coleta finalizada com {coletados} IDs únicos.")

        # Detalhamento
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
        if os.path.exists(estado_path):
            os.remove(estado_path)
            print("🔓 lock_status.json removido")
        print(f"✅ Fim da extração em {datetime.now().isoformat()}")
