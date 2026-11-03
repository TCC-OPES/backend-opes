
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models.deletion import ProtectedError

from core.models import Cartao
from core.serializers import CartaoSerializer


class CartaoView(APIView):

    permission_classes = [IsAuthenticated]

    # Listar cartões do usuário
    def get(self, request):

        cartoes = Cartao.objects.filter(
            usuario=request.user
        )

        serializer = CartaoSerializer(
            cartoes,
            many=True
        )

        return Response(serializer.data)

    # Cadastrar novo cartão
    def post(self, request):

        serializer = CartaoSerializer(
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

    # Atualizar apenas cartões pertencentes ao usuário autenticado
    @transaction.atomic
    def patch(self, request, pk=None):
        if pk is None:
            return Response({'erro': 'Informe o ID do cartão.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cartao = Cartao.objects.select_for_update().get(pk=pk, usuario=request.user)
        except Cartao.DoesNotExist:
            return Response({'erro': 'Cartão não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CartaoSerializer(cartao, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # Excluir cartão pelo ID
    def delete(self, request, pk=None):

        if pk is None:
            return Response(
                {'erro': 'Informe o ID do cartão.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cartao = Cartao.objects.get(
                pk=pk,
                usuario=request.user
            )

        except Cartao.DoesNotExist:
            return Response(
                {'erro': 'Cartão não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            cartao.delete()
        except ProtectedError:
            return Response(
                {'erro': 'Esse cartão possui compras vinculadas. Exclua ou altere essas transações antes de remover o cartão.'},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
