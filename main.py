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
def extrair_ativos():
    try:
        print("🟢 Rota /extrair-ativos acionada")
        executar_extracao_ativos()
        return {"status": "sucesso", "mensagem": "Todos os ativos extraídos com sucesso"}
    except Exception as e:
        print(f"❌ Erro em /extrair-ativos: {e}")
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-pausados")
def extrair_pausados(offset: int = Query(0), limit: int = Query(1000)):
    try:
        print(f"🟢 Rota /extrair-pausados acionada | offset={offset} limit={limit}")
        executar_extracao_pausados(offset=offset, limit=limit)
        return {"status": "sucesso", "mensagem": f"Pausados extraídos com offset={offset} e limit={limit}"}
    except Exception as e:
        print(f"❌ Erro em /extrair-pausados: {e}")
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-finalizados")
def extrair_finalizados(offset: int = Query(0), limit: int = Query(1000)):
    try:
        print(f"🟢 Rota /extrair-finalizados acionada | offset={offset} limit={limit}")
        executar_extracao_finalizados(offset=offset, limit=limit)
        return {"status": "sucesso", "mensagem": f"Finalizados extraídos com offset={offset} e limit={limit}"}
    except Exception as e:
        print(f"❌ Erro em /extrair-finalizados: {e}")
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-perguntas-respondidas")
def extrair_perguntas():
    try:
        print("🟢 Rota /extrair-perguntas-respondidas acionada")
        executar_extracao_perguntas()
        return {"status": "sucesso", "mensagem": "Perguntas extraídas com sucesso"}
    except Exception as e:
        print(f"❌ Erro em /extrair-perguntas-respondidas: {e}")
        return {"status": "erro", "mensagem": str(e)}
