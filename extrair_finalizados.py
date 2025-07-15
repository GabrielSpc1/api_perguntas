from utils_meli import extrair_por_status

def executar_extracao_finalizados():
    extrair_por_status("closed", "produtos_finalizados.jsonl")
