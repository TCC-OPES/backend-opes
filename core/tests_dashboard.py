from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from core.models import Transacao
from core.models.recorrencia import Recorrencia


class DashboardDadosReaisTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(cpf='11223344556', email='dashboard@teste.com', password='12345Segura!')
        self.other = User.objects.create_user(cpf='11223344557', email='outra@teste.com', password='12345Segura!')
        self.client.force_authenticate(self.user)

    def test_sem_lancamentos_nao_inventa_saldos(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(str(response.data['resumo']['resultado_registrado'])), Decimal('0'))
        self.assertEqual(response.data['resumo']['total_transacoes'], 0)
        self.assertEqual(len(response.data['serie_mensal']), 6)
        self.assertTrue(all(Decimal(str(x['resultado'])) == 0 for x in response.data['serie_mensal']))
        self.assertEqual(len(response.data['gastos_semanais']), 7)

    def test_agrega_somente_dados_do_usuario(self):
        Transacao.objects.create(usuario=self.user, titulo='Salário', categoria='Trabalho', tipo='receita', valor=Decimal('1500'), data=timezone.now())
        Transacao.objects.create(usuario=self.user, titulo='Compras', categoria='Mercado', tipo='despesa', valor=Decimal('400'), data=timezone.now())
        Transacao.objects.create(usuario=self.other, titulo='Outra', categoria='Geral', tipo='despesa', valor=Decimal('700'), data=timezone.now())
        Recorrencia.objects.create(usuario=self.user, titulo='Internet', categoria='Casa', tipo='despesa',
            valor=Decimal('100'), frequencia='semanal', primeiro_vencimento=timezone.localdate())
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(str(response.data['resumo']['resultado_registrado'])), Decimal('1100'))
        self.assertEqual(response.data['resumo']['total_transacoes'], 2)
        self.assertTrue(response.data['proximas'])
        self.assertEqual(response.data['proximas'][0]['titulo'], 'Internet')
