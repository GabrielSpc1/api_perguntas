from utils_meli import extrair_por_status

def executar_extracao_pausados():
    extrair_por_status("paused", "produtos_pausados.jsonl")
