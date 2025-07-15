import os
import requests
import json
from datetime import datetime
from github import Github
import time

# === Variáveis de ambiente ===
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"
ARQUIVO_GITHUB = "perguntas_respondidas_meli.jsonl"

def renovar_token():
    print("🔐 Renovando token de acesso...")
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    token = response.json()["access_token"]
    print("✅ Token renovado com sucesso.")
    return token

def buscar_user_id(token):
    print("👤 Buscando ID do usuário...")
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["id"]

def buscar_todos_anuncios(user_id, token):
    print("📦 Buscando todos os anúncios (ativos, pausados e finalizados)...")
    headers = {"Authorization": f"Bearer {token}"}
    status_list = ["active", "paused", "closed"]
    all_ids = []

    for status in status_list:
        print(f"🔎 Coletando anúncios com status: {status}")
        offset = 0
        while True:
            url = f"https://api.mercadolibre.com/users/{user_id}/items/search?status={status}&limit=50&offset={offset}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            ids = data.get("results", [])
            if not ids:
                break

            all_ids.extend(ids)
            print(f"➕ Total até agora: {len(all_ids)}")
            offset += 50
            time.sleep(0.1)

    print(f"✅ Total de anúncios coletados: {len(all_ids)}")
    return all_ids

def buscar_perguntas_por_item(item_id, token):
    url = f"https://api.mercadolibre.com/questions/search?item_id={item_id}&status=ANSWERED"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("questions", [])

def salvar_jsonl(dados, nome_arquivo):
    print(f"💾 Salvando {len(dados)} pares pergunta-resposta em {nome_arquivo}")
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        for item in dados:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

def upload_github(nome_arquivo_local, nome_arquivo_remoto):
    print("🚀 Enviando para o GitHub...")
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
    print("✅ Upload concluído.")

def executar_extracao_perguntas():
    token = renovar_token()
    user_id = buscar_user_id(token)
    item_ids = buscar_todos_anuncios(user_id, token)

    perguntas_final = []
    print("🧠 Iniciando coleta de perguntas respondidas...")

    for i, item_id in enumerate(item_ids):
        print(f"🔄 [{i+1}/{len(item_ids)}] Anúncio: {item_id}")
        try:
            perguntas = buscar_perguntas_por_item(item_id, token)
            for p in perguntas:
                perguntas_final.append({
                    "pergunta": p["text"],
                    "resposta": p.get("answer", {}).get("text", ""),
                    "item_id": item_id
                })
        except Exception as e:
            print(f"❌ Erro ao processar {item_id}: {str(e)}")
        time.sleep(0.1)

    if not perguntas_final:
        raise ValueError("⚠️ Nenhuma pergunta respondida foi encontrada.")

    nome_arquivo = "perguntas_respondidas_meli.jsonl"
    salvar_jsonl(perguntas_final, nome_arquivo)
    upload_github(nome_arquivo, ARQUIVO_GITHUB)
    print("✅ Extração de perguntas respondidas finalizada.")
