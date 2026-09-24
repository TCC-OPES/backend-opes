import os

import requests

PLUGGY_BASE_URL = os.getenv("PLUGGY_BASE_URL", "https://api.pluggy.ai")


def obter_api_key():
    client_id = os.getenv("PLUGGY_CLIENT_ID")
    client_secret = os.getenv("PLUGGY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("Credenciais da Pluggy não configuradas.")
    url = f"{PLUGGY_BASE_URL}/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()["apiKey"]


def criar_connect_token(api_key, user_id, item_id=None):
    url = f"{PLUGGY_BASE_URL}/connect_token"
    payload = {"options": {"clientUserId": str(user_id), "avoidDuplicates": True}}
    if item_id:
        payload["itemId"] = item_id

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()["accessToken"]


def buscar_item(api_key, item_id):
    url = f"{PLUGGY_BASE_URL}/items/{item_id}"
    headers = {"X-API-KEY": api_key}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


def _buscar_paginas(api_key, path, params):
    headers = {"X-API-KEY": api_key}
    resultados = []
    pagina = 1
    while True:
        response = requests.get(
            f"{PLUGGY_BASE_URL}/{path}",
            params={**params, "page": pagina},
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        dados = response.json()
        resultados.extend(dados["results"])
        if pagina >= dados.get("totalPages", 1):
            return resultados
        pagina += 1


def buscar_contas(api_key, item_id):
    return _buscar_paginas(api_key, "accounts", {"itemId": item_id})


def buscar_transacoes(api_key, account_id):
    return _buscar_paginas(api_key, "transactions", {"accountId": account_id})
