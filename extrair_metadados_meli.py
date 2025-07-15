import os
import requests
import json
import time
from datetime import datetime
from github import Github

# === Variáveis de ambiente ===
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"
ARQUIVO_GITHUB = "produtos_meli_metadados.jsonl"

def renovar_token():
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def buscar_user_id(token):
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()["id"]

def buscar_todos_os_ids(user_id, token, status):
    print(f"[INFO] Buscando anúncios com status: {status}")
    headers = {"Authorization": f"Bearer {token}"}
    base_url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    params = {
        "status": status,
        "search_type": "scan",
        "limit": 100
    }

    all_ids = []
    scroll_id = None

    while True:
        if scroll_id:
            params["scroll_id"] = scroll_id

        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"[ERRO] {response.status_code}: {response.text}")

        result = response.json()
        ids = result.get("results", [])
        scroll_id = result.get("scroll_id")

        if not ids:
            break

        all_ids.extend(ids)
        print(f"  → {len(all_ids)} coletados até agora ({status})")
        time.sleep(0.1)

    return all_ids

def detalhar_anuncio(item_id, token):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[AVISO] Falha ao obter detalhes do {item_id}: {response.status_code}")
        return None
    return response.json()

def salvar_jsonl(dados, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        for item in dados:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

def upload_github(nome_arquivo_local, nome_arquivo_remoto):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    with open(nome_arquivo_local, "r", encoding="utf-8") as f:
        conteudo_texto = f.read()

    try:
        arq = repo.get_contents(nome_arquivo_remoto, ref="main")
        repo.update_file(
            nome_arquivo_remoto,
            f"update {nome_arquivo_remoto} {datetime.now().isoformat()}",
            conteudo_texto,
            arq.sha,
            branch="main"
        )
    except:
        repo.create_file(
            nome_arquivo_remoto,
            f"create {nome_arquivo_remoto} {datetime.now().isoformat()}",
            conteudo_texto,
            branch="main"
        )

def executar_extracao():
    access_token = renovar_token()
    user_id = buscar_user_id(access_token)

    todos_ids = []
    for status in ["active", "paused", "closed"]:
        ids = buscar_todos_os_ids(user_id, access_token, status)
        todos_ids.extend(ids)

    print(f"[INFO] Total geral de anúncios coletados (ativos, pausados, finalizados): {len(set(todos_ids))}")

    detalhes = []
    for idx, item_id in enumerate(todos_ids):
        detalhe = detalhar_anuncio(item_id, access_token)
        if detalhe:
            detalhes.append(detalhe)
        if idx % 50 == 0:
            print(f"  → {idx} detalhados...")
        time.sleep(0.1)

    nome_arquivo = "produtos_meli_metadados.jsonl"
    salvar_jsonl(detalhes, nome_arquivo)
    upload_github(nome_arquivo, ARQUIVO_GITHUB)

    print(f"[SUCESSO] {len(detalhes)} anúncios salvos em {nome_arquivo}")

# Se desejar rodar localmente:
# executar_extracao()

