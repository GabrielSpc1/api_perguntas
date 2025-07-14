from fastapi import FastAPI
from extrair_metadados_meli import executar_extracao
from extrair_perguntas_respondidas import executar_extracao_perguntas

app = FastAPI()

@app.get("/")
def raiz():
    return {"mensagem": "API de extração Mercado Livre ativa."}

@app.get("/extrair-metadados")
def extrair_metadados():
    try:
        executar_extracao()
        return {"status": "sucesso", "mensagem": "Metadados extraídos e enviados para o GitHub"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-perguntas-respondidas")
def extrair_perguntas():
    try:
        executar_extracao_perguntas()
        return {"status": "sucesso", "mensagem": "Perguntas respondidas extraídas e enviadas para o GitHub"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
