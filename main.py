
from fastapi import FastAPI
from extrair_metadados_meli import executar_extracao

app = FastAPI()

@app.get("/extrair-metadados")
def extrair_metadados():
    try:
        executar_extracao()
        return {"status": "sucesso", "mensagem": "Metadados extraídos e enviados para o GitHub"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
