import os
import requests
import json
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
    response.raise_for_status()
    return response.json()["id"]

def buscar_todos_anuncios(user_id, token):
    url_base = f"https://api.mercadolibre.com/users/{user_id}/items/all?limit=50"
    headers = {"Authorization": f"Bearer {token}"}
    anuncios = []
    offset = 0

    while True:
        url = f"{url_base}&offset={offset}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        dados = response.json()
        resultados = dados.get("results", [])
        if not resultados:
            break
        anuncios.extend(resultados)
        offset += 50
        if offset >= dados.get("paging", {}).get("total", 0):
            break

    print(f"[INFO] Total de anúncios coletados: {len(anuncios)}")
    return anuncios

def detalhar_anuncio(item_id, token):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
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
    ids = buscar_todos_anuncios(user_id, access_token)
    detalhes = [detalhar_anuncio(anuncio_id, access_token) for anuncio_id in ids]
    nome_arquivo = "produtos_meli_metadados.jsonl"
    salvar_jsonl(detalhes, nome_arquivo)
    upload_github(nome_arquivo, ARQUIVO_GITHUB)

