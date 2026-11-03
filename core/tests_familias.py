from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Familia, MembroFamilia, ConviteFamilia


class FamiliasConvitesAPITests(APITestCase):
    def setUp(self):
        Usuario = get_user_model()
        self.criador = Usuario.objects.create_user(
            cpf='11122233344', email='criador@exemplo.com',
            name='Criador', password='senha12345'
        )
        self.convidado = Usuario.objects.create_user(
            cpf='22233344455', email='convidado@exemplo.com',
            name='Convidado', password='senha12345'
        )
        self.terceiro = Usuario.objects.create_user(
            cpf='33344455566', email='terceiro@exemplo.com',
            name='Terceiro', password='senha12345'
        )
        self.client.force_authenticate(user=self.criador)
        resposta = self.client.post(
            '/api/familias/', {'nome': 'Família Teste'}, format='json'
        )
        self.assertEqual(resposta.status_code, 201, resposta.data)
        self.familia = Familia.objects.get(pk=resposta.data['id'])
        self.url_membros = f'/api/familias/{self.familia.pk}/membros/'

    def convidar(self, papel='membro', email='convidado@exemplo.com'):
        return self.client.post(
            self.url_membros, {'email': email, 'papel': papel}, format='json'
        )

    def test_criador_e_administrador_e_pode_convidar_email_cadastrado(self):
        membro = MembroFamilia.objects.get(
            familia=self.familia, usuario=self.criador
        )
        self.assertEqual(membro.papel, 'admin')
        resposta = self.convidar(email='CONVIDADO@EXEMPLO.COM')
        self.assertEqual(resposta.status_code, 201, resposta.data)
        self.assertEqual(resposta.data['status'], 'pendente')
        self.assertFalse(MembroFamilia.objects.filter(
            familia=self.familia, usuario=self.convidado
        ).exists())
        self.assertEqual(self.convidar().status_code, 409)
        self.assertEqual(ConviteFamilia.objects.filter(
            familia=self.familia, usuario=self.convidado,
            status=ConviteFamilia.PENDENTE
        ).count(), 1)

    def test_aceitar_convida_somente_destinatario_e_lista_familia(self):
        convite_id = self.convidar().data['id']
        caminho = f'/api/familias/convites/{convite_id}/responder/'
        self.assertEqual(self.client.post(
            caminho, {'acao': 'aceitar'}, format='json'
        ).status_code, 404)
        self.client.force_authenticate(user=self.convidado)
        self.assertEqual(len(self.client.get('/api/familias/convites/').data), 1)
        resposta = self.client.post(caminho, {'acao': 'aceitar'}, format='json')
        self.assertEqual(resposta.status_code, 200, resposta.data)
        self.assertEqual(resposta.data['status'], 'aceito')
        self.assertEqual(self.client.post(
            caminho, {'acao': 'aceitar'}, format='json'
        ).status_code, 409)
        membro = MembroFamilia.objects.get(
            familia=self.familia, usuario=self.convidado
        )
        self.assertEqual(membro.papel, 'membro')
        familias = self.client.get('/api/familias/')
        self.assertEqual(familias.status_code, 200)
        self.assertEqual(len(familias.data), 1)
        self.assertEqual(len(familias.data[0]['membros']), 2)
        self.assertEqual(len(self.client.get(self.url_membros).data), 2)

    def test_recusar_convite_nao_adiciona_membro(self):
        id_convite = self.convidar('dependente').data['id']
        self.client.force_authenticate(user=self.convidado)
        resposta = self.client.post(
            f'/api/familias/convites/{id_convite}/responder/',
            {'acao': 'recusar'}, format='json'
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data['status'], 'recusado')
        self.assertFalse(MembroFamilia.objects.filter(
            familia=self.familia, usuario=self.convidado
        ).exists())
        self.assertEqual(self.client.get('/api/familias/').data, [])
        self.client.force_authenticate(user=self.criador)
        self.assertEqual(self.convidar().status_code, 201)

    def test_sem_permissao_para_convidar_ou_remover_terceiros(self):
        convite = self.convidar().data['id']
        self.client.force_authenticate(user=self.convidado)
        self.client.post(
            f'/api/familias/convites/{convite}/responder/',
            {'acao': 'aceitar'}, format='json'
        )
        self.assertEqual(self.client.post(
            self.url_membros,
            {'email': self.terceiro.email}, format='json'
        ).status_code, 403)
        self.assertEqual(self.client.get(
            f'/api/familias/{self.familia.pk}/convites/'
        ).status_code, 403)
        criador_membro = MembroFamilia.objects.get(
            familia=self.familia, usuario=self.criador
        )
        self.assertEqual(self.client.delete(
            f'/api/familias/{self.familia.pk}/membros/{criador_membro.pk}/'
        ).status_code, 403)
        self.client.force_authenticate(user=self.criador)
        self.assertEqual(self.client.delete(
            f'/api/familias/{self.familia.pk}/membros/{criador_membro.pk}/'
        ).status_code, 400)
        convidado_membro = MembroFamilia.objects.get(
            familia=self.familia, usuario=self.convidado
        )
        self.assertEqual(self.client.delete(
            f'/api/familias/{self.familia.pk}/membros/{convidado_membro.pk}/'
        ).status_code, 204)

    def test_membro_pode_sair_sozinho(self):
        convite_id = self.convidar().data['id']
        self.client.force_authenticate(user=self.convidado)
        self.client.post(f'/api/familias/convites/{convite_id}/responder/',
                         {'acao': 'aceitar'}, format='json')
        membro = MembroFamilia.objects.get(
            familia=self.familia, usuario=self.convidado
        )
        resposta = self.client.delete(
            f'/api/familias/{self.familia.pk}/membros/{membro.pk}/'
        )
        self.assertEqual(resposta.status_code, 204)
        self.assertEqual(self.client.get('/api/familias/').data, [])

    def test_cancelar_convite_impede_aceite(self):
        convite_id = self.convidar().data['id']
        self.assertEqual(self.client.delete(
            f'/api/familias/{self.familia.pk}/convites/{convite_id}/'
        ).status_code, 204)
        self.client.force_authenticate(user=self.convidado)
        self.assertEqual(self.client.get('/api/familias/convites/').data, [])
        self.assertEqual(self.client.post(
            f'/api/familias/convites/{convite_id}/responder/',
            {'acao': 'aceitar'}, format='json'
        ).status_code, 409)

    def test_isolamento_e_validacao_de_dados(self):
        self.assertEqual(self.convidar(email='inexistente@exemplo.com').status_code, 404)
        self.assertEqual(self.convidar(papel='admin').status_code, 400)
        self.assertEqual(self.convidar(email=self.criador.email).status_code, 400)
        self.client.force_authenticate(user=self.terceiro)
        self.assertEqual(self.client.get(self.url_membros).status_code, 404)
        self.assertEqual(self.client.post(
            self.url_membros, {'email': self.convidado.email}, format='json'
        ).status_code, 404)
        self.assertEqual(self.client.get('/api/familias/').data, [])

    def test_sem_autenticacao(self):
        self.client.force_authenticate(user=None)
        self.assertIn(self.client.get('/api/familias/convites/').status_code, (401, 403))
        self.assertIn(self.client.get(self.url_membros).status_code, (401, 403))
