import json
from datetime import datetime

def salvar_dados(dados, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def salvar_lock_status(scroll_id, total_coletado, timestamp, em_execucao):
    status = {
        "scroll_id": scroll_id,
        "total_coletado": total_coletado,
        "timestamp": timestamp,
        "em_execucao": em_execucao
    }
    with open("lock_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

def carregar_lock_status():
    try:
        with open("lock_status.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"em_execucao": False}
