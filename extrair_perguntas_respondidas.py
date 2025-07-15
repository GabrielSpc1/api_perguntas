import os
import requests
import json
from github import Github
from datetime import datetime

# === Variáveis de ambiente ===
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"
NOME_ARQUIVO = "perguntas_respondidas_meli.jsonl"

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

def buscar_perguntas_respondidas(user_id, token):
    perguntas = []
    limit = 50
    offset = 0

    while True:
        url = f"https://api.mercadolibre.com/users/{user_id}/questions/search?status=ANSWERED&limit={limit}&offset={offset}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        perguntas.extend(data.get("questions", []))

        total = data.get("total", 0)
        offset += limit
        if offset >= total:
            break

    return perguntas

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

def executar_extracao_perguntas():
    token = renovar_token()
    user_id = buscar_user_id(token)
    perguntas = buscar_perguntas_respondidas(user_id, token)
    salvar_jsonl(perguntas, NOME_ARQUIVO)
    upload_github(NOME_ARQUIVO, NOME_ARQUIVO)
