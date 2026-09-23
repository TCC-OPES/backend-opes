import requests
from django.conf import settings

BASE_URL = 'https://api.pluggy.ai'
TIMEOUT = 30


class PluggyError(Exception):
    pass


def _request(method, path, api_key=None, **kwargs):
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['X-API-KEY'] = api_key
    try:
        resposta = requests.request(
            method,
            f'{BASE_URL}{path}',
            headers=headers,
            timeout=TIMEOUT,
            **kwargs,
        )
        resposta.raise_for_status()
    except requests.RequestException as exc:
        raise PluggyError(str(exc)) from exc
    return resposta.json()


def obter_api_key():
    dados = _request(
        'POST',
        '/auth',
        json={
            'clientId': settings.PLUGGY_CLIENT_ID,
            'clientSecret': settings.PLUGGY_CLIENT_SECRET,
        },
    )
    return dados['apiKey']


def criar_connect_token(user_id):
    api_key = obter_api_key()
    dados = _request(
        'POST',
        '/connect_token',
        api_key=api_key,
        json={'options': {'clientUserId': str(user_id)}},
    )
    return dados['accessToken']


def obter_item(api_key, item_id):
    return _request('GET', f'/items/{item_id}', api_key=api_key)


def listar_contas(api_key, item_id):
    dados = _request('GET', '/accounts', api_key=api_key, params={'itemId': item_id})
    return dados['results']


def listar_transacoes(api_key, conta_id):
    pagina = 1
    while True:
        dados = _request(
            'GET',
            '/transactions',
            api_key=api_key,
            params={'accountId': conta_id, 'pageSize': 500, 'page': pagina},
        )
        for transacao in dados['results']:
            yield transacao
        if pagina >= dados.get('totalPages', 1):
            break
        pagina += 1