import os

import requests

PLUGGY_BASE_URL = os.getenv("PLUGGY_BASE_URL", "https://api.pluggy.ai")


def obter_api_key():
    client_id = os.getenv("PLUGGY_CLIENT_ID")
    client_secret = os.getenv("PLUGGY_CLIENT_SECRET")
    url = f"{PLUGGY_BASE_URL}/auth"
    payload = {"clientId": client_id, "clientSecret": client_secret}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["apiKey"]


def criar_connect_token(api_key, item_id=None):
    url = f"{PLUGGY_BASE_URL}/connect_token"
    payload = {}
    if item_id:
        payload["itemId"] = item_id

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["accessToken"]


def buscar_item(api_key, item_id):
    url = f"{PLUGGY_BASE_URL}/items/{item_id}"
    headers = {"X-API-KEY": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def buscar_contas(api_key, item_id):
    url = f"{PLUGGY_BASE_URL}/accounts?itemId={item_id}"
    headers = {"X-API-KEY": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["results"]


def buscar_transacoes(api_key, account_id):
    url = f"{PLUGGY_BASE_URL}/transactions?accountId={account_id}"
    headers = {"X-API-KEY": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["results"]