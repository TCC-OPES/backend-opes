from datetime import date
from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core import pluggy
from core.models.openfinance import ConexaoBancaria, TransacaoImportada
from core.serializers.openfinance import (
    ConexaoBancariaSerializer,
    TransacaoImportadaSerializer,
)


class ConnectTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = pluggy.criar_connect_token(request.user.id)
        except pluggy.PluggyError:
            return Response(
                {'detail': 'Falha ao comunicar com o provedor de dados bancários.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({'connectToken': token})


class ConexaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conexoes = ConexaoBancaria.objects.filter(usuario=request.user)
        serializer = ConexaoBancariaSerializer(conexoes, many=True)
        return Response(serializer.data)

    def post(self, request):
        item_id = request.data.get('itemId')
        if not item_id:
            return Response(
                {'detail': 'itemId é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        conexao, _ = ConexaoBancaria.objects.get_or_create(
            item_id=item_id,
            defaults={'usuario': request.user},
        )
        if conexao.usuario_id != request.user.id:
            return Response(
                {'detail': 'Conexão pertence a outro usuário.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ConexaoBancariaSerializer(conexao)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SincronizarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, conexao_id):
        conexao = get_object_or_404(
            ConexaoBancaria,
            id=conexao_id,
            usuario=request.user,
        )
        importadas = 0
        try:
            api_key = pluggy.obter_api_key()
            item = pluggy.obter_item(api_key, conexao.item_id)
            if item.get('status') != 'UPDATED':
                return Response(
                    {'status': item.get('status')},
                    status=status.HTTP_409_CONFLICT,
                )
            for conta in pluggy.listar_contas(api_key, conexao.item_id):
                for transacao in pluggy.listar_transacoes(api_key, conta['id']):
                    TransacaoImportada.objects.update_or_create(
                        id_externo=transacao['id'],
                        defaults={
                            'conexao': conexao,
                            'conta_id': conta['id'],
                            'descricao': (transacao.get('description') or '')[:255],
                            'valor': Decimal(str(transacao['amount'])),
                            'tipo': transacao.get('type') or '',
                            'categoria': (transacao.get('category') or '')[:100],
                            'data': date.fromisoformat(transacao['date'][:10]),
                        },
                    )
                    importadas += 1
        except pluggy.PluggyError:
            return Response(
                {'detail': 'Falha ao comunicar com o provedor de dados bancários.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({'importadas': importadas})


class TransacaoImportadaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transacoes = TransacaoImportada.objects.filter(
            conexao__usuario=request.user
        )
        serializer = TransacaoImportadaSerializer(transacoes, many=True)
        return Response(serializer.data)