from fastapi import FastAPI, Query
from extrair_ativos import executar_extracao_ativos
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


@app.get("/extrair-perguntas-respondidas")
def extrair_perguntas():
    try:
        print("🟢 Rota /extrair-perguntas-respondidas acionada")
        executar_extracao_perguntas()
        return {"status": "sucesso", "mensagem": "Perguntas extraídas com sucesso"}
    except Exception as e:
        print(f"❌ Erro em /extrair-perguntas-respondidas: {e}")
        return {"status": "erro", "mensagem": str(e)}
