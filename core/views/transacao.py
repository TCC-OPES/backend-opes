from decimal import Decimal
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from core.models import Transacao, Cartao
from core.serializers import TransacaoSerializer


def ajustar_limites(antiga, nova):
    """Usado dentro de atomic: devolve gasto antigo e aplica o novo, travando cartões."""
    deltas = {}
    for item, sinal in ((antiga, -1), (nova, 1)):
        if item and item.tipo == 'despesa' and item.metodo_pagamento == 'credito' and item.cartao_id:
            deltas[item.cartao_id] = deltas.get(item.cartao_id, Decimal('0.00')) + sinal * item.valor

    for cartao in Cartao.objects.select_for_update().filter(pk__in=sorted(deltas)).order_by('pk'):
        utilizado = cartao.valor_utilizado + deltas[cartao.pk]
        if utilizado < 0:
            raise ValidationError({'valor': 'A alteração deixaria o limite utilizado negativo. Revise os valores do cartão.'})
        if utilizado > cartao.limite_total:
            raise ValidationError({'valor': f'Limite insuficiente no cartão {cartao.nome}.'})
        cartao.valor_utilizado = utilizado
        cartao.save(update_fields=['valor_utilizado'])


class TransacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        transacoes = Transacao.objects.filter(usuario=request.user).order_by('-data', '-pk')
        tipo = request.query_params.get('tipo')
        if tipo and tipo != 'todas':
            transacoes = transacoes.filter(tipo=tipo)
        return Response(TransacaoSerializer(transacoes, many=True, context={'request': request}).data)

    @transaction.atomic
    def post(self, request, pk=None):
        serializer = TransacaoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        nova = Transacao(**serializer.validated_data, usuario=request.user)
        ajustar_limites(None, nova)
        nova.save()
        return Response(TransacaoSerializer(nova, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def patch(self, request, pk=None):
        if pk is None:
            return Response({'erro': 'Informe o ID da transação.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            antiga = Transacao.objects.select_for_update().get(pk=pk, usuario=request.user)
        except Transacao.DoesNotExist:
            return Response({'erro': 'Transação não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransacaoSerializer(antiga, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        nova = Transacao(
            id=antiga.id,
            usuario=antiga.usuario,
            titulo=serializer.validated_data.get('titulo', antiga.titulo),
            categoria=serializer.validated_data.get('categoria', antiga.categoria),
            tipo=serializer.validated_data.get('tipo', antiga.tipo),
            valor=serializer.validated_data.get('valor', antiga.valor),
            data=serializer.validated_data.get('data', antiga.data),
            metodo_pagamento=serializer.validated_data.get('metodo_pagamento', antiga.metodo_pagamento),
            cartao=serializer.validated_data.get('cartao', antiga.cartao),
        )
        ajustar_limites(antiga, nova)
        serializer.save()
        return Response(TransacaoSerializer(antiga, context={'request': request}).data)

    @transaction.atomic
    def delete(self, request, pk=None):
        if pk is None:
            return Response({'erro': 'Informe o ID da transação.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            antiga = Transacao.objects.select_for_update().get(pk=pk, usuario=request.user)
        except Transacao.DoesNotExist:
            return Response({'erro': 'Transação não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        ajustar_limites(antiga, None)
        antiga.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
