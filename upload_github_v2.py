import os
from github import Github, InputGitAuthor
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Caminho local do arquivo JSONL
LOCAL_JSONL_PATH = os.path.join(os.path.dirname(__file__), "dataset_meli.jsonl")

# Nome do repositório e caminho-alvo no repositório
REPO_NAME = "GabrielSpc1/api_perguntas"
TARGET_FILE_PATH = "dataset_meli.jsonl"

# Token de acesso ao GitHub (use variável de ambiente para segurança)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def upload_para_github():
    try:
        if not os.path.exists(LOCAL_JSONL_PATH):
            raise FileNotFoundError(f"Arquivo não encontrado: {LOCAL_JSONL_PATH}")

        with open(LOCAL_JSONL_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)

        # Pega o conteúdo atual do arquivo (se existir) para obter o SHA
        try:
            existing_file = repo.get_contents(TARGET_FILE_PATH)
            sha = existing_file.sha
            logging.info("📄 Arquivo existente encontrado no repositório.")
        except:
            sha = None
            logging.info("🆕 Arquivo ainda não existe no repositório. Será criado.")

        # Cria ou atualiza o arquivo
        commit_message = f"📦 Atualização automática via upload_github.py - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        repo.create_file(
            path=TARGET_FILE_PATH,
            message=commit_message,
            content=content,
            sha=sha,
            branch="main",
            author=InputGitAuthor("Desmonte AI", "no-reply@desmonte.ai")
        ) if sha is None else repo.update_file(
            path=TARGET_FILE_PATH,
            message=commit_message,
            content=content,
            sha=sha,
            branch="main",
            author=InputGitAuthor("Desmonte AI", "no-reply@desmonte.ai")
        )

        logging.info("✅ Upload para o GitHub concluído com sucesso.")
    
    except Exception as e:
        logging.error(f"❌ Erro ao fazer upload para o GitHub: {e}")
        raise
