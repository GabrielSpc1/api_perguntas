import os
import time
import json
from github import Github
from datetime import datetime
from utils_meli import renovar_token, buscar_user_id, detalhar_anuncio
import requests


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"

def buscar_anuncios_paginado(user_id, token, status="active"):
    url_base = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    headers = {"Authorization": f"Bearer {token}"}
    offset = 0
    limit = 100
    todos_ids = []

    while True:
        params = {
            "status": status,
            "offset": offset,
            "limit": limit
        }
        response = requests.get(url_base, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        resultados = data.get("results", [])
        print(f"[INFO] Página offset={offset}, coletados {len(resultados)} anúncios.")
        todos_ids.extend(resultados)

        if len(resultados) < limit:
            break  # Última página
        offset += limit
        time.sleep(0.5)

    return todos_ids

def executar_extracao_ativos():
    token = renovar_token()
    user_id = buscar_user_id(token)
    ids = buscar_anuncios_paginado(user_id, token, status="active")

    detalhes = []
    for i, anuncio_id in enumerate(ids):
        try:
            detalhes.append(detalhar_anuncio(anuncio_id, token))
            if i % 50 == 0:
                print(f"[INFO] Detalhado {i}/{len(ids)} anúncios.")
            time.sleep(0.2)
        except Exception as e:
            print(f"[ERRO] Falha ao detalhar {anuncio_id}: {e}")

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
        repo.update_file(nome_arquivo_remoto, f"update {nome_arquivo_remoto} {datetime.now().isoformat()}", conteudo, arq.sha, branch="main")
    except:
        repo.create_file(nome_arquivo_remoto, f"create {nome_arquivo_remoto} {datetime.now().isoformat()}", conteudo, branch="main")
