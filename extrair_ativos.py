from utils_meli import extrair_por_status

def executar_extracao_ativos():
    extrair_por_status("active", "produtos_ativos.jsonl")
