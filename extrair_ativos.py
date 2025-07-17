import os
import time
import json
import requests
from github import Github
from datetime import datetime
from utils_meli import renovar_token, buscar_user_id

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "GabrielSpc1/api_perguntas"

def is_locked_remotamente():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file = repo.get_contents("lock_status.json", ref="main")
        content = json.loads(file.decoded_content.decode())
        return content.get("em_execucao", False)
    except:
        return False

def set_lock_remoto(valor: bool):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    content = json.dumps({"em_execucao": valor})
    try:
        arq = repo.get_contents("lock_status.json", ref="main")
        repo.update_file("lock_status.json", f"update lock {datetime.now().isoformat()}", content, arq.sha, branch="main")
    except:
        repo.create_file("lock_status.json", f"create lock {datetime.now().isoformat()}", content, branch="main")

def executar_extracao_ativos():
    if is_locked_remotamente():
        print("🚫 Extração já em execução (lock remoto GitHub). Abortando.")
        return

    set_lock_remoto(True)
    print(f"🟢 Início da extração em {datetime.now().isoformat()}")
    start_time = time.time()

    try:
        token = renovar_token()
        user_id = buscar_user_id(token)
        headers = {"Authorization": f"Bearer {token}"}

        limit = 100
        scroll_id = None
        all_ids = []

        print("🚀 Iniciando extração com SCAN + scroll_id...")

        while True:
            if time.time() - start_time > 900:
                print("⏱️ Tempo máximo de execução atingido (15 minutos). Abortando.")
                break

            params = {
                "status": "active",
                "search_type": "scan",
                "limit": limit
            }
            if scroll_id:
                params["scroll_id"] = scroll_id

            try:
                response = requests.get(
                    f"https://api.mercadolibre.com/users/{user_id}/items/search",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
            except Exception as e:
                print(f"❌ Erro na requisição SCAN: {e}")
                break

            data = response.json()
            ids = data.get("results", [])
            scroll_id = data.get("scroll_id")

            if not ids:
                print(f"🛑 Fim do loop SCAN: último scroll_id = {scroll_id}")
                break

            all_ids.extend(ids)
            print(f"📦 Coletados até agora: {len(all_ids)} anúncios ativos...")

            # Salva progresso parcial
            with open("progresso_parcial.json", "w", encoding="utf-8") as f:
                json.dump({"ids": all_ids, "scroll_id": scroll_id}, f, ensure_ascii=False)

            time.sleep(0.1)

        print(f"✅ Coleta finalizada com {len(all_ids)} IDs únicos.")
        detalhes = []
        for i, item_id in enumerate(all_ids):
            try:
                r = requests.get(f"https://api.mercadolibre.com/items/{item_id}", headers=headers, timeout=30)
                r.raise_for_status()
                detalhes.append(r.json())
                if i % 50 == 0:
                    print(f"🔍 Detalhado {i}/{len(all_ids)} anúncios.")
                time.sleep(0.2)
            except Exception as e:
                print(f"❌ Erro ao detalhar {item_id}: {e}")

        nome_arquivo = f"ativos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            for item in detalhes:
                json.dump(item, f, ensure_ascii=False)
                f.write("\n")

        # Upload GitHub
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        try:
            arq = repo.get_contents(nome_arquivo, ref="main")
            repo.update_file(nome_arquivo, f"update {nome_arquivo} {datetime.now().isoformat()}", conteudo, arq.sha, branch="main")
        except:
            repo.create_file(nome_arquivo, f"create {nome_arquivo} {datetime.now().isoformat()}", conteudo, branch="main")

    except Exception as e:
        print(f"❌ Erro inesperado durante execução: {e}")

    finally:
        set_lock_remoto(False)
        print(f"🔓 Lock removido (remoto)")
        print(f"✅ Fim da extração em {datetime.now().isoformat()}")
