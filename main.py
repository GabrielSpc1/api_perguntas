from fastapi import FastAPI
from extrair_ativos import executar_extracao_ativos
from extrair_perguntas_respondidas import executar_extracao_perguntas
from threading import Thread
from datetime import datetime

app = FastAPI()

@app.get("/")
def raiz():
    return {"mensagem": "API de extração Mercado Livre ativa."}

@app.get("/extrair-ativos")
def extrair_ativos():
    try:
        print(f"🟢 Rota /extrair-ativos acionada em {datetime.now().isoformat()}")
        Thread(target=executar_extracao_ativos).start()
        return {"status": "sucesso", "mensagem": "Extração iniciada em segundo plano"}
    except Exception as e:
        print(f"❌ Erro ao iniciar extração de ativos: {e}")
        return {"status": "erro", "mensagem": str(e)}

@app.get("/extrair-perguntas-respondidas")
def extrair_perguntas():
    try:
        print(f"🟢 Rota /extrair-perguntas-respondidas acionada em {datetime.now().isoformat()}")
        executar_extracao_perguntas()
        return {"status": "sucesso", "mensagem": "Perguntas extraídas com sucesso"}
    except Exception as e:
        print(f"❌ Erro em /extrair-perguntas-respondidas: {e}")
        return {"status": "erro", "mensagem": str(e)}
