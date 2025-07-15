from fastapi import FastAPI
from extrair_metadados_meli import executar_extracao_por_status
from extrair_perguntas_respondidas import executar_extracao_perguntas

app = FastAPI()

@app.get("/")
def raiz():
    return {"mensagem": "API de extração Mercado Livre ativa."}

@app.get("/extrair-metadados-ativos")
def extrair_ativos():
    try:
        executar_extracao_por_status("active", "produtos_meli_ativos.jsonl", "produtos_meli_ativos.jsonl")
        return {"status": "sucesso", "mensagem": "Ativos extraídos e enviados para o GitHub"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-metadados-pausados")
def extrair_pausados():
    try:
        executar_extracao_por_status("paused", "produtos_meli_pausados.jsonl", "produtos_meli_pausados.jsonl")
        return {"status": "sucesso", "mensagem": "Pausados extraídos e enviados para o GitHub"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-metadados-finalizados")
def extrair_finalizados():
    try:
        executar_extracao_por_status("closed", "produtos_meli_finalizados.jsonl", "produtos_meli_finalizados.jsonl")
        return {"status": "sucesso", "mensagem": "Finalizados extraídos e enviados para o GitHub"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-perguntas-respondidas")
def extrair_perguntas():
    try:
        executar_extracao_perguntas()
        return {"status": "sucesso", "mensagem": "Perguntas respondidas extraídas e enviadas para o GitHub"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
