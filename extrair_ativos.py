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
        print(f"📦 Coletados até agora: {len(all_ids)} anúncios ativos...")
        time.sleep(0.1)

    print(f"✅ Coleta finalizada com {len(all_ids)} IDs únicos.")
    
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

    nome_arquivo = "ativos_completos.jsonl"
    salvar_jsonl(detalhes, nome_arquivo)
    upload_github(nome_arquivo, nome_arquivo)

def salvar_jsonl(dados, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        for item in dados:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

def upload_github(nome_arquivo_local, nome_arquivo_remoto):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    with open(nome_arquivo_local, "r", encoding="utf-8") as f:
        conteudo = f.read()

    try:
        arq = repo.get_contents(nome_arquivo_remoto, ref="main")
        repo.update_file(
            nome_arquivo_remoto,
            f"update {nome_arquivo_remoto} {datetime.now().isoformat()}",
            conteudo,
            arq.sha,
            branch="main"
        )
    except:
        repo.create_file(
            nome_arquivo_remoto,
            f"create {nome_arquivo_remoto} {datetime.now().isoformat()}",
            conteudo,
            branch="main"
        )
