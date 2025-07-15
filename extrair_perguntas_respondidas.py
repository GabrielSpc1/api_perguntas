import os
import requests
import json

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
USER_ID = os.getenv("USER_ID", "162089212")  # ID fixo opcional
ARQUIVO_SAIDA = "perguntas_respondidas_meli.jsonl"

def buscar_perguntas_completas(user_id, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    perguntas = []
    offset = 0
    limit = 50

    while True:
        url = "https://api.mercadolibre.com/my/received_questions/search"
        params = {
            "seller_id": user_id,
            "status": "ANSWERED",
            "limit": limit,
            "offset": offset
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Erro {response.status_code}: {response.text}")

        data = response.json()
        resultados = data.get("questions", [])
        if not resultados:
            break

        perguntas.extend(resultados)
        offset += limit
        print(f"[INFO] Coletadas até agora: {len(perguntas)} perguntas")

    return perguntas

def salvar_jsonl(dados, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        for item in dados:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

def executar_extracao_perguntas():
    if not ACCESS_TOKEN:
        raise ValueError("A variável ACCESS_TOKEN não está definida.")
    perguntas = buscar_perguntas_completas(USER_ID, ACCESS_TOKEN)
    salvar_jsonl(perguntas, ARQUIVO_SAIDA)
    print(f"[SUCESSO] {len(perguntas)} perguntas salvas em {ARQUIVO_SAIDA}")
