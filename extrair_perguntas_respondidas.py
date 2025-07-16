import os
import requests
import json
from datetime import datetime
from github import Github
from utils_meli import renovar_token, buscar_user_id

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"
ARQUIVO_GITHUB = "perguntas_respondidas.jsonl"

def buscar_perguntas_respondidas(user_id, token):
    url_base = f"https://api.mercadolibre.com/questions/search"
    headers = {"Authorization": f"Bearer {token}"}
    offset = 0
    limit = 50
    todas = []

    while True:
        params = {
            "seller_id": user_id,
            "status": "ANSWERED",
            "limit": limit,
            "offset": offset
        }
        response = requests.get(url_base, headers=headers, params=params)
        data = response.json()
        perguntas = data.get("questions", [])
        todas.extend(perguntas)

        if len(perguntas) < limit:
            break
        offset += limit

    return todas

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
    salvar_jsonl(perguntas, ARQUIVO_GITHUB)
    upload_github(ARQUIVO_GITHUB, ARQUIVO_GITHUB)

