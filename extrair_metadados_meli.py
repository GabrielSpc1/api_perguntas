
import os
import requests
import json
import base64
from datetime import datetime
from github import Github

# === Variáveis de ambiente ===
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"
ARQUIVO_GITHUB = "produtos_meli_metadados.jsonl"

# === Função para obter novo access_token ===
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

# === Buscar ID do usuário (dinâmico) ===
def buscar_user_id(token):
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()["id"]

# === Buscar anúncios ativos ===
def buscar_anuncios_ativos(user_id, token):
    url = f"https://api.mercadolibre.com/users/{user_id}/items/search?status=active&limit=50"
    headers = {"Authorization": f"Bearer {token}"}
    anuncios = []
    offset = 0

    while True:
        response = requests.get(f"{url}&offset={offset}", headers=headers)
        dados = response.json()
        anuncios.extend(dados.get("results", []))
        if offset + 50 >= dados.get("paging", {}).get("total", 0):
            break
        offset += 50

    return anuncios

# === Buscar detalhes de cada anúncio ===
def detalhar_anuncio(item_id, token):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# === Salvar JSONL local ===
def salvar_jsonl(dados, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        for item in dados:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

# === Upload para GitHub ===
def upload_github(nome_arquivo_local, nome_arquivo_remoto):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    with open(nome_arquivo_local, "rb") as f:
        conteudo = f.read()
    conteudo_base64 = base64.b64encode(conteudo).decode("utf-8")

    try:
        arq = repo.get_contents(nome_arquivo_remoto, ref="main")
        repo.update_file(
            nome_arquivo_remoto,
            f"update {nome_arquivo_remoto} {datetime.now().isoformat()}",
            conteudo_base64,
            arq.sha,
            branch="main",
            encoding="base64"
        )
    except:
        repo.create_file(
            nome_arquivo_remoto,
            f"create {nome_arquivo_remoto} {datetime.now().isoformat()}",
            conteudo_base64,
            branch="main",
            encoding="base64"
        )

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    print("🔑 Renovando token...")
    access_token = renovar_token()

    print("👤 Buscando ID do usuário...")
    user_id = buscar_user_id(access_token)

    print("🔄 Buscando anúncios ativos...")
    ids = buscar_anuncios_ativos(user_id, access_token)

    print(f"✅ {len(ids)} anúncios encontrados. Extraindo detalhes...")
    detalhes = [detalhar_anuncio(anuncio_id, access_token) for anuncio_id in ids]

    nome_arquivo = "produtos_meli_metadados.jsonl"
    salvar_jsonl(detalhes, nome_arquivo)

    print("☁️ Enviando arquivo para o GitHub...")
    upload_github(nome_arquivo, ARQUIVO_GITHUB)
    print("✅ Extração e envio concluídos com sucesso.")
