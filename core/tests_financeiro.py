from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from core.models import Transacao, MetaFinanceira, Investimento


class FluxosFinanceirosTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(cpf='22334455667', email='financeiro@teste.com', password='Teste#123')
        self.other = User.objects.create_user(cpf='22334455668', email='outro@teste.com', password='Teste#123')
        self.client.force_authenticate(self.user)

    def test_transacao_cadastro_listagem_exclusao_e_isolamento(self):
        response = self.client.post('/api/transacoes/', {
            'titulo': 'Mercado', 'categoria': 'Alimentação', 'tipo': 'despesa',
            'valor': '42.35', 'data': '2026-10-28',
        })
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']
        self.assertEqual(len(self.client.get('/api/transacoes/').data), 1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/transacoes/').data, [])
        self.assertEqual(self.client.delete(f'/api/transacoes/{pk}/').status_code, 404)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f'/api/transacoes/{pk}/').status_code, 204)
        self.assertFalse(Transacao.objects.filter(pk=pk).exists())

    def test_meta_cadastro_edicao_exclusao_e_isolamento(self):
        data = {
            'titulo': 'Reserva', 'categoria': 'seguranca', 'descricao': 'Reserva financeira',
            'valor_objetivo': '1200.00', 'valor_atual': '100.00', 'valor_mensal': '100.00',
            'data_limite': '2027-12-31',
        }
        response = self.client.post('/api/metas/', data)
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']
        response = self.client.put(f'/api/metas/{pk}/', {'valor_atual': '250.00'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(str(response.data['valor_atual'])), Decimal('250.00'))
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f'/api/metas/{pk}/').status_code, 404)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f'/api/metas/{pk}/').status_code, 204)
        self.assertFalse(MetaFinanceira.objects.filter(pk=pk).exists())

    def test_investimento_cadastro_listagem_exclusao_e_isolamento(self):
        response = self.client.post('/api/investimentos/', {
            'nome': 'Tesouro', 'tipo': 'renda_fixa', 'valor_investido': '1000.00',
            'rentabilidade': '8.00', 'cor': '#b7835d',
        })
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get('/api/investimentos/').data, [])
        self.assertEqual(self.client.delete(f'/api/investimentos/{pk}/').status_code, 404)
        self.client.force_authenticate(self.user)
        self.assertEqual(len(self.client.get('/api/investimentos/').data), 1)
        self.assertEqual(self.client.delete(f'/api/investimentos/{pk}/').status_code, 204)
        self.assertFalse(Investimento.objects.filter(pk=pk).exists())
