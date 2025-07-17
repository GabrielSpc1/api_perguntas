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
            status = json.load(f)
            # Garante que todos os campos esperados existam
            return {
                "scroll_id": status.get("scroll_id"),
                "total_coletado": status.get("total_coletado", 0),
                "timestamp": status.get("timestamp", datetime.now().isoformat()),
                "em_execucao": status.get("em_execucao", False)
            }
    except FileNotFoundError:
        return {
            "scroll_id": None,
            "total_coletado": 0,
            "timestamp": datetime.now().isoformat(),
            "em_execucao": False
        }

