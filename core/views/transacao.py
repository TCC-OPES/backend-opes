
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import Transacao
from core.serializers import TransacaoSerializer


class TransacaoView(APIView):
    permission_classes = [IsAuthenticated]

    # Listar transações
    def get(self, request, pk=None):
        tipo = request.query_params.get('tipo')
        transacoes = Transacao.objects.filter(
            usuario=request.user
        )        
        transacoes = Transacao.objects.filter(usuario=request.user).order_by("-data", "-pk")
        if tipo and tipo != 'todas':
            transacoes = transacoes.filter(tipo=tipo)

        serializer = TransacaoSerializer(
            transacoes,
            many=True
        )
        return Response(serializer.data)

    # Criar transação
    def post(self, request, pk=None):
        serializer = TransacaoSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(
            usuario=request.user
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    # Excluir transação pelo ID
    def delete(self, request, pk=None):
        if pk is None:
            return Response(
                {'erro': 'Informe o ID da transação.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transacao = Transacao.objects.get(
                pk=pk,
                usuario=request.user
            )

        except Transacao.DoesNotExist:
            return Response(
                {'erro': 'Transação não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        transacao.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
