
import os
import requests
import json
from datetime import datetime
from github import Github

# Variáveis de ambiente
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"
ARQUIVO_GITHUB = "perguntas_respondidas_meli.jsonl"

# === Autenticação ===
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

# === Buscar ID do usuário ===
def buscar_user_id(token):
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()["id"]

# === Buscar perguntas respondidas ===
def buscar_perguntas_respondidas(user_id, token):
    offset = 0
    limit = 50
    todas = []
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        url = f"https://api.mercadolibre.com/questions/search?seller_id={user_id}&status=ANSWERED&offset={offset}&limit={limit}"
        resp = requests.get(url, headers=headers)
        data = resp.json()
        todas.extend(data.get("questions", []))

        if len(data.get("questions", [])) < limit:
            break
        offset += limit

    return todas

# === Salvar JSONL local ===
def salvar_jsonl(lista, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        for item in lista:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

# === Upload para GitHub ===
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

# === Função principal ===
def executar_extracao_perguntas():
    token = renovar_token()
    user_id = buscar_user_id(token)
    perguntas = buscar_perguntas_respondidas(user_id, token)

    lista_formatada = [
        {
            "pergunta": p["text"],
            "resposta": p["answer"]["text"] if p.get("answer") else "",
            "item_id": p.get("item_id"),
            "question_id": p.get("id"),
            "date_created": p.get("date_created")
        }
        for p in perguntas if p.get("answer")
    ]

    nome_arquivo = "perguntas_respondidas_meli.jsonl"
    salvar_jsonl(lista_formatada, nome_arquivo)
    upload_github(nome_arquivo, ARQUIVO_GITHUB)
