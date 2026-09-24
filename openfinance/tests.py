from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import User
from openfinance.models import ConexaoBancaria, TransacaoImportada
from openfinance.pluggy import buscar_transacoes


class OpenFinanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(cpf="12345678901", email="one@example.com", password="test-password")
        self.other = User.objects.create_user(cpf="12345678902", email="two@example.com", password="test-password")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("openfinance.views.obter_api_key", return_value="api-key")
    @patch("openfinance.views.criar_connect_token", return_value="connect-token")
    def test_connect_token_is_scoped_to_user(self, criar, _key):
        response = self.client.post("/api/openfinance/connect-token/", {}, format="json")
        self.assertEqual(response.status_code, 200)
        criar.assert_called_once_with("api-key", self.user.pk, None)

        ConexaoBancaria.objects.create(user=self.other, item_id="foreign-item")
        response = self.client.post("/api/openfinance/connect-token/", {"itemId": "foreign-item"}, format="json")
        self.assertEqual(response.status_code, 404)

    @patch("openfinance.views.obter_api_key", return_value="api-key")
    @patch("openfinance.views.buscar_item")
    def test_cannot_save_another_users_item(self, buscar_item, _key):
        buscar_item.return_value = {"clientUserId": str(self.other.pk), "connector": {"name": "Banco"}}
        response = self.client.post("/api/openfinance/salvar-conexao/", {"itemId": "foreign-item"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ConexaoBancaria.objects.exists())

    @patch("openfinance.views.obter_api_key", return_value="api-key")
    @patch("openfinance.views.buscar_item")
    @patch("openfinance.views.buscar_contas", return_value=[{"id": "account-1"}])
    @patch("openfinance.views.buscar_transacoes")
    def test_sync_is_idempotent_and_visible_only_to_owner(self, buscar_transacoes_mock, _contas, buscar_item, _key):
        ConexaoBancaria.objects.create(user=self.user, item_id="own-item", instituicao_nome="Banco")
        buscar_item.return_value = {"clientUserId": str(self.user.pk), "status": "UPDATED"}
        buscar_transacoes_mock.return_value = [{
            "id": "transaction-1", "description": "Mercado", "amount": -25.5,
            "date": "2026-09-22T12:00:00Z", "type": "DEBIT", "category": "Compras",
        }]
        for esperado in (1, 0):
            response = self.client.post("/api/openfinance/sincronizar/", {"itemId": "own-item"}, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["novas_transacoes"], esperado)
        self.assertEqual(TransacaoImportada.objects.count(), 1)
        response = self.client.get("/api/transacoes/")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]["valor"]), "25.50")
        self.assertEqual(response.data[0]["tipo"], "despesa")
        self.client.force_authenticate(user=self.other)
        self.assertEqual(self.client.get("/api/transacoes/").data, [])
        self.assertEqual(self.client.get("/api/openfinance/conexoes/").data, [])

    @patch("openfinance.pluggy.requests.get")
    def test_fetches_all_transaction_pages(self, get):
        get.return_value.raise_for_status.return_value = None
        get.return_value.json.side_effect = [
            {"results": [{"id": "first"}], "totalPages": 2},
            {"results": [{"id": "second"}], "totalPages": 2},
        ]
        self.assertEqual([t["id"] for t in buscar_transacoes("key", "account")], ["first", "second"])
        self.assertEqual(get.call_args_list[1].kwargs["params"]["page"], 2)
