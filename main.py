from fastapi import FastAPI
from extrair_ativos import executar_extracao_ativos
from extrair_pausados import executar_extracao_pausados
from extrair_finalizados import executar_extracao_finalizados
from extrair_perguntas_respondidas import executar_extracao_perguntas

app = FastAPI()

@app.get("/")
def raiz():
    return {"mensagem": "API de extração Mercado Livre ativa."}

@app.get("/extrair-ativos")
def ativos():
    try:
        executar_extracao_ativos()
        return {"status": "sucesso", "mensagem": "Ativos extraídos com sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-pausados")
def pausados():
    try:
        executar_extracao_pausados()
        return {"status": "sucesso", "mensagem": "Pausados extraídos com sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-finalizados")
def finalizados():
    try:
        executar_extracao_finalizados()
        return {"status": "sucesso", "mensagem": "Finalizados extraídos com sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-perguntas-respondidas")
def perguntas():
    try:
        executar_extracao_perguntas()
        return {"status": "sucesso", "mensagem": "Perguntas extraídas com sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
