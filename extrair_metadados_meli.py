import os
import requests
import json
import time
from datetime import datetime
from github import Github

# Variáveis de ambiente
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"

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

def coletar_anuncios_por_status(token, user_id, status):
    headers = {"Authorization": f"Bearer {token}"}
    all_item_ids = []
    scroll_id = None
    limit = 100

    while True:
        url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
        params = {
            "status": status,
            "search_type": "scan",
            "limit": limit
        }
        if scroll_id:
            params["scroll_id"] = scroll_id

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Erro {response.status_code}: {response.text}")

        data = response.json()
        ids = data.get("results", [])
        scroll_id = data.get("scroll_id")

        if not ids:
            break

        all_item_ids.extend(ids)
        time.sleep(0.1)

    return all_item_ids

def detalhar_anuncio(item_id, token):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
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
        repo.update_file(nome_arquivo_remoto, f"update {nome_arquivo_remoto} {datetime.now().isoformat()}", conteudo_texto, arq.sha, branch="main")
    except:
        repo.create_file(nome_arquivo_remoto, f"create {nome_arquivo_remoto} {datetime.now().isoformat()}", conteudo_texto, branch="main")

def executar_extracao_por_status(status, nome_arquivo_local, nome_arquivo_remoto):
    access_token = renovar_token()
    user_id = buscar_user_id(access_token)
    item_ids = coletar_anuncios_por_status(access_token, user_id, status)
    detalhes = [detalhar_anuncio(i, access_token) for i in item_ids]
    salvar_jsonl(detalhes, nome_arquivo_local)
    upload_github(nome_arquivo_local, nome_arquivo_remoto)

