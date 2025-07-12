import os
from github import Github, InputGitAuthor

def upload_para_github():
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = "GabrielSpc1/api_perguntas"
    BRANCH_NAME = "main"
    LOCAL_PATH = "/tmp/respostas_validadas.jsonl"
    REMOTE_PATH = "dataset_meli.jsonl"
    COMMIT_MESSAGE = "Atualização via moderação Hugging Face"

    if not GITHUB_TOKEN:
        raise ValueError("Token do GitHub não encontrado. Configure a variável GITHUB_TOKEN.")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    with open(LOCAL_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        file = repo.get_contents(REMOTE_PATH, ref=BRANCH_NAME)
        sha = file.sha
    except:
        sha = None

    repo.update_file(
        path=REMOTE_PATH,
        message=COMMIT_MESSAGE,
        content=content,
        sha=sha,
        branch=BRANCH_NAME,
        author=InputGitAuthor("Bot Sportcar", "no-reply@sportcar.com")
    )
