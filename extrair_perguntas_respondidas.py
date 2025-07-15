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
ARQUIVO_GITHUB = "perguntas_respondidas_meli.jsonl"

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

def buscar_perguntas(user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    perguntas = []
    limit = 50
    offset = 0

    while True:
        url = f"https://api.mercadolibre.com/my/received_questions/search?seller_id={user_id}&status=ANSWERED&offset={offset}&limit={limit}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Erro {response.status_code}: {response.text}")
            break

        data = response.json()
        perguntas.extend(data.get("questions", []))

        if offset + limit >= data.get("total", 0):
            break

        offset += limit

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

def executar_extracao_perguntas():
    access_token = renovar_token()
    user_id = buscar_user_id(access_token)
    perguntas = buscar_perguntas(user_id, access_token)
    nome_arquivo = "perguntas_respondidas_meli.jsonl"
    salvar_jsonl(perguntas, nome_arquivo)
    upload_github(nome_arquivo, ARQUIVO_GITHUB)
