from django.test import TestCase
from django.urls import Resolver404, resolve
from rest_framework.test import APIClient

from core.models import User
from openfinance.models import ConexaoBancaria, TransacaoImportada


class RemovedOpenFinanceTests(TestCase):
    def test_bank_endpoints_are_not_available(self):
        for endpoint in ("connect-token", "salvar-conexao", "conexoes", "sincronizar"):
            with self.subTest(endpoint=endpoint), self.assertRaises(Resolver404):
                resolve(f"/api/openfinance/{endpoint}/")

    def test_legacy_bank_data_is_preserved_but_not_listed(self):
        user = User.objects.create_user(cpf="12345678901", email="one@example.com", password="test-password")
        connection = ConexaoBancaria.objects.create(user=user, item_id="legacy")
        TransacaoImportada.objects.create(conexao=connection, external_id="old", descricao="Legado", valor=10,
                                         data="2026-10-01T12:00:00Z", tipo="receita")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/transacoes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        self.assertEqual(TransacaoImportada.objects.count(), 1)
        response = client.post("/api/transacoes/", {"titulo": "Manual", "categoria": "Outros", "tipo": "receita",
                                                 "valor": "25.00", "data": "2026-10-21T12:00:00Z"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(client.get("/api/transacoes/").data), 1)
