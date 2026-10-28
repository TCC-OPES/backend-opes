from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import Transacao
from core.models.recorrencia import Recorrencia, OcorrenciaRecorrente
from core.views.recorrencia import vencimentos


class CalendarioRecorrenciaTests(SimpleTestCase):
    def test_dia_31_usa_ultimo_dia_do_mes(self):
        r = Recorrencia(primeiro_vencimento=date(2026, 1, 31), frequencia='mensal')
        self.assertEqual(list(vencimentos(r, date(2026, 1, 1), date(2026, 3, 31))), [
            date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)
        ])

    def test_anual_em_ano_bissexto(self):
        r = Recorrencia(primeiro_vencimento=date(2024, 2, 29), frequencia='anual')
        self.assertEqual(list(vencimentos(r, date(2024, 1, 1), date(2026, 12, 31))), [
            date(2024, 2, 29), date(2025, 2, 28), date(2026, 2, 28)
        ])


class RecorrenciaAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(cpf='11122233344', email='um@teste.com', password='teste12345')
        self.other = User.objects.create_user(cpf='55566677788', email='dois@teste.com', password='teste12345')
        self.client.force_authenticate(self.user)

    def test_confirmacao_idempotente_e_sem_vazamento(self):
        r = Recorrencia.objects.create(
            usuario=self.user, titulo='Internet', categoria='Casa', tipo='despesa',
            valor=Decimal('99.90'), frequencia='mensal', primeiro_vencimento=date(2026, 1, 31)
        )
        url = '/api/recorrencias/ocorrencias/?inicio=2026-02-01&fim=2026-02-28'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vencimento'], '2026-02-28')
        oc = OcorrenciaRecorrente.objects.get(recorrencia=r)
        path = f'/api/recorrencias/ocorrencias/{oc.pk}/confirmar/'
        self.assertEqual(self.client.post(path).status_code, 200)
        self.assertEqual(self.client.post(path).status_code, 200)
        self.assertEqual(Transacao.objects.filter(usuario=self.user).count(), 1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.post(path).status_code, 404)
        self.assertEqual(self.client.get('/api/recorrencias/').data, [])

    def test_pausar_preserva_pagamentos_e_cancela_previsoes_futuras(self):
        from django.utils import timezone
        inicio = timezone.localdate()
        r = Recorrencia.objects.create(
            usuario=self.user, titulo='Assinatura', categoria='Serviço',
            tipo='despesa', valor=Decimal('25.00'),
            frequencia='semanal', primeiro_vencimento=inicio,
        )
        fim = inicio + __import__('datetime').timedelta(days=14)
        response = self.client.get('/api/recorrencias/ocorrencias/', {
            'inicio': inicio.isoformat(), 'fim': fim.isoformat()
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        primeiro = response.data[0]['id']
        self.assertEqual(self.client.post(f'/api/recorrencias/ocorrencias/{primeiro}/confirmar/').status_code, 200)
        self.assertEqual(self.client.patch(f'/api/recorrencias/{r.pk}/', {'ativa': False}).status_code, 200)
        self.assertEqual(OcorrenciaRecorrente.objects.filter(recorrencia=r).count(), 1)
        self.assertEqual(Transacao.objects.filter(usuario=self.user).count(), 1)

    def test_isolamento_e_validacao_de_valores(self):
        invalida = {
            'titulo': 'Inválida', 'categoria': 'Geral', 'tipo': 'despesa',
            'valor': '-5.00', 'frequencia': 'mensal', 'primeiro_vencimento': '2026-11-01',
        }
        self.assertEqual(self.client.post('/api/recorrencias/', invalida).status_code, 400)
        invalida['valor'] = '19.90'
        result = self.client.post('/api/recorrencias/', invalida)
        self.assertEqual(result.status_code, 201)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/recorrencias/{result.data['id']}/").status_code, 404)

    def test_parcelas_geram_ultimo_vencimento_e_nao_mais_datas(self):
        payload = {
            'titulo': 'Notebook', 'categoria': 'Equipamentos', 'tipo': 'despesa',
            'valor': '250.00', 'frequencia': 'mensal',
            'primeiro_vencimento': '2026-01-31', 'numero_parcelas': 3,
        }
        created = self.client.post('/api/recorrencias/', payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['data_fim'], '2026-03-31')
        self.assertEqual(created.data['numero_parcelas'], 3)
        response = self.client.get('/api/recorrencias/ocorrencias/', {
            'inicio': '2026-01-01', 'fim': '2026-06-30',
        })
        self.assertEqual([x['vencimento'] for x in response.data], [
            '2026-01-31', '2026-02-28', '2026-03-31',
        ])

    def test_nao_aceita_parcelamento_anual(self):
        payload = {
            'titulo': 'Seguro', 'categoria': 'Geral', 'tipo': 'despesa',
            'valor': '80.00', 'frequencia': 'anual',
            'primeiro_vencimento': '2026-11-02', 'numero_parcelas': 4,
        }
        self.assertEqual(self.client.post('/api/recorrencias/', payload).status_code, 400)
