from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from core.models import Cartao, Transacao


class PagamentosCreditoTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            cpf='12345678901', email='teste@exemplo.com', password='senha-forte'
        )
        self.client.force_authenticate(user=self.user)
        self.cartao = Cartao.objects.create(
            usuario=self.user,
            banco='Banco Teste',
            nome='Principal',
            limite_total=Decimal('1000.00'),
            valor_utilizado=Decimal('100.00'),
            vencimento='2026-11-15',
            cor='#295B83',
        )

    def _despesa(self, valor='200.00'):
        return {
            'titulo': 'Mercado', 'categoria': 'Alimentação', 'tipo': 'despesa',
            'valor': valor, 'data': '2026-10-28T12:00:00Z',
            'metodo_pagamento': 'credito', 'cartao': self.cartao.id,
        }

    def _utilizado(self):
        self.cartao.refresh_from_db()
        return self.cartao.valor_utilizado

    def test_criacao_edicao_e_exclusao_reconciliam_limite(self):
        criada = self.client.post('/api/transacoes/', self._despesa(), format='json')
        self.assertEqual(criada.status_code, 201, criada.data)
        self.assertEqual(self._utilizado(), Decimal('300.00'))
        pk = criada.data['id']

        editada = self.client.patch(
            f'/api/transacoes/{pk}/', {'valor': '350.00'}, format='json'
        )
        self.assertEqual(editada.status_code, 200, editada.data)
        self.assertEqual(self._utilizado(), Decimal('450.00'))

        removida = self.client.delete(f'/api/transacoes/{pk}/')
        self.assertEqual(removida.status_code, 204)
        self.assertEqual(self._utilizado(), Decimal('100.00'))

    def test_limite_insuficiente_nao_cria_transacao(self):
        resposta = self.client.post('/api/transacoes/', self._despesa('950.00'), format='json')
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(self._utilizado(), Decimal('100.00'))
        self.assertEqual(Transacao.objects.count(), 0)

    def test_cartao_de_outro_usuario_e_rejeitado(self):
        outro = get_user_model().objects.create_user(
            cpf='10987654321', email='outro@exemplo.com', password='senha-forte'
        )
        estrangeiro = Cartao.objects.create(
            usuario=outro, banco='Outro', nome='Outro',
            limite_total=Decimal('999.00'), vencimento='2026-12-10'
        )
        dados = self._despesa()
        dados['cartao'] = estrangeiro.pk
        resposta = self.client.post('/api/transacoes/', dados, format='json')
        self.assertEqual(resposta.status_code, 400)

    def test_cor_persiste_no_backend(self):
        resposta = self.client.patch(
            f'/api/cartoes/{self.cartao.id}/',
            {'cor': '#7D4655'}, format='json'
        )
        self.assertEqual(resposta.status_code, 200, resposta.data)
        self.cartao.refresh_from_db()
        self.assertEqual(self.cartao.cor, '#7D4655')

    def test_cartao_com_transacoes_nao_pode_ser_excluido(self):
        criada = self.client.post('/api/transacoes/', self._despesa(), format='json')
        self.assertEqual(criada.status_code, 201)
        removida = self.client.delete(f'/api/cartoes/{self.cartao.id}/')
        self.assertEqual(removida.status_code, 409)
        self.assertTrue(Cartao.objects.filter(pk=self.cartao.id).exists())
