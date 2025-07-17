
from fastapi import FastAPI, Query
from extrair_ativos import executar_extracao_ativos
from extrair_pausados import executar_extracao_pausados
from extrair_finalizados import executar_extracao_finalizados
from extrair_perguntas_respondidas import executar_extracao_perguntas

app = FastAPI()

@app.get("/")
def raiz():
    return {"mensagem": "API de extração Mercado Livre ativa."}

@app.get("/extrair-ativos")
def ativos(offset: int = Query(0), limit: int = Query(1000)):
    try:
        executar_extracao_ativos(offset=offset, limit=limit)
        return {"status": "sucesso", "mensagem": f"Ativos extraídos com offset={offset} e limit={limit}"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-pausados")
def pausados(offset: int = Query(0), limit: int = Query(1000)):
    try:
        executar_extracao_pausados(offset=offset, limit=limit)
        return {"status": "sucesso", "mensagem": f"Pausados extraídos com offset={offset} e limit={limit}"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-finalizados")
def finalizados(offset: int = Query(0), limit: int = Query(1000)):
    try:
        executar_extracao_finalizados(offset=offset, limit=limit)
        return {"status": "sucesso", "mensagem": f"Finalizados extraídos com offset={offset} e limit={limit}"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-perguntas-respondidas")
def perguntas():
    try:
        executar_extracao_perguntas()
        return {"status": "sucesso", "mensagem": "Perguntas extraídas com sucesso"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
