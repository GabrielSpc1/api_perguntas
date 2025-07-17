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

    offset = 0
    limit = 50
    todos_detalhes = []

    while True:
        url = f"https://api.mercadolibre.com/users/{user_id}/items/search?status=active&offset={offset}&limit={limit}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        ids = data.get("results", [])
        print(f"🔄 Offset {offset} | Itens recebidos: {len(ids)}")

        if not ids:
            break

        for i, item_id in enumerate(ids):
            try:
                r = requests.get(f"https://api.mercadolibre.com/items/{item_id}", headers=headers)
                r.raise_for_status()
                todos_detalhes.append(r.json())
                time.sleep(0.2)
            except Exception as e:
                print(f"❌ Erro ao detalhar {item_id}: {e}")

        if len(ids) < limit:
            break

        offset += limit

    nome_arquivo = "ativos_completos.jsonl"
    salvar_jsonl(todos_detalhes, nome_arquivo)
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
