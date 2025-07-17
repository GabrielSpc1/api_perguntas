import os
import time
import json
import requests
from github import Github
from datetime import datetime
from utils_meli import renovar_token, buscar_user_id, detalhar_anuncio

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"

def executar_extracao_ativos():
    if os.path.exists("lock_ativos.txt"):
        print("🚫 Já em execução. Abortando nova tentativa.")
        return
    with open("lock_ativos.txt", "w") as f:
        f.write("locked")

    print(f"🟢 Início da extração em {datetime.now().isoformat()}")

    try:
        token = renovar_token()
        user_id = buscar_user_id(token)
        headers = {"Authorization": f"Bearer {token}"}

        limit = 100
        scroll_id = None
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
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout na requisição SCAN (scroll_id={scroll_id}). Abortando.")
                break
            except Exception as e:
                print(f"❌ Erro durante SCAN: {e}")
                break

            data = response.json()
            ids = data.get("results", [])
            scroll_id = data.get("scroll_id")

            if not ids:
                print(f"🛑 Fim do loop SCAN: último scroll_id = {scroll_id}")
                break

            all_ids.extend(ids)
            print(f"📦 Coletados até agora: {len(all_ids)} anúncios ativos...")
            time.sleep(0.1)

        print(f"✅ Coleta finalizada com {len(all_ids)} IDs únicos.")

        detalhes = []
        for i, item_id in enumerate(all_ids):
            try:
                r = requests.get(f"https://api.mercadolibre.com/items/{item_id}", headers=headers, timeout=30)
                r.raise_for_status()
                detalhes.append(r.json())
                if i % 50 == 0:
                    print(f"🔍 Detalhado {i}/{len(all_ids)} anúncios.")
                time.sleep(0.2)
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout ao detalhar {item_id}. Pulando...")
            except Exception as e:
                print(f"❌ Erro ao detalhar {item_id}: {e}")

        nome_arquivo = f"ativos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        salvar_jsonl(detalhes, nome_arquivo)
        upload_github(nome_arquivo, nome_arquivo)

    except Exception as e:
        print(f"❌ Erro inesperado durante execução: {e}")

    finally:
        if os.path.exists("lock_ativos.txt"):
            os.remove("lock_ativos.txt")
            print("🔓 Lock removido")
        print(f"✅ Fim da extração em {datetime.now().isoformat()}")
