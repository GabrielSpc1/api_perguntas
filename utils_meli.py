import os
import requests
import json
from github import Github
from datetime import datetime

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

def buscar_anuncios(user_id, token, status):
    url = f"https://api.mercadolibre.com/users/{user_id}/items/search?status={status}&search_type=scan&limit=100"
    headers = {"Authorization": f"Bearer {token}"}
    anuncios = []
    scroll_id = None

    while True:
        final_url = url + (f"&scroll_id={scroll_id}" if scroll_id else "")
        response = requests.get(final_url, headers=headers)
        data = response.json()
        anuncios.extend(data.get("results", []))
        scroll_id = data.get("scroll_id")
        print(f"[INFO] Coletados até agora: {len(anuncios)} anúncios ativos...")
        
        if not data.get("results"):
            break

    return anuncios

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
        conteudo = f.read()

    try:
        arq = repo.get_contents(nome_arquivo_remoto, ref="main")
        repo.update_file(nome_arquivo_remoto, f"update {nome_arquivo_remoto} {datetime.now().isoformat()}", conteudo, arq.sha, branch="main")
    except:
        repo.create_file(nome_arquivo_remoto, f"create {nome_arquivo_remoto} {datetime.now().isoformat()}", conteudo, branch="main")

def extrair_por_status(status, nome_arquivo):
    token = renovar_token()
    user_id = buscar_user_id(token)
    ids = buscar_anuncios(user_id, token, status)
    detalhes = [detalhar_anuncio(anuncio_id, token) for anuncio_id in ids]
    salvar_jsonl(detalhes, nome_arquivo)
    upload_github(nome_arquivo, nome_arquivo)
