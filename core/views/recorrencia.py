from calendar import monthrange
from datetime import date, timedelta, datetime, time
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Transacao
from core.models.recorrencia import Recorrencia, OcorrenciaRecorrente
from core.serializers.recorrencia import RecorrenciaSerializer, OcorrenciaSerializer


def vencimentos(recorrencia, inicio, fim):
    """Mantém o dia original da mensalidade; dia 31 vira último dia do mês."""
    primeiro = recorrencia.primeiro_vencimento
    limite = min(fim, recorrencia.data_fim) if recorrencia.data_fim else fim
    if limite < primeiro:
        return
    if recorrencia.frequencia == 'semanal':
        data = primeiro
        if inicio > data:
            data += timedelta(weeks=max(0, (inicio - data).days // 7))
        while data <= limite:
            if data >= inicio:
                yield data
            data += timedelta(days=7)
    else:
        meses_passo = 12 if recorrencia.frequencia == 'anual' else 1
        indice = 0
        while True:
            total = (primeiro.year * 12 + primeiro.month - 1) + indice * meses_passo
            ano, mes0 = divmod(total, 12)
            dia = min(primeiro.day, monthrange(ano, mes0 + 1)[1])
            data = date(ano, mes0 + 1, dia)
            if data > limite:
                break
            if data >= inicio:
                yield data
            indice += 1


class RecorrenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        qs = Recorrencia.objects.filter(usuario=request.user)
        if pk is not None:
            return Response(RecorrenciaSerializer(get_object_or_404(qs, pk=pk)).data)
        return Response(RecorrenciaSerializer(qs, many=True).data)

    def post(self, request, pk=None):
        if pk is not None:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = RecorrenciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk=None):
        obj = get_object_or_404(Recorrencia, pk=pk, usuario=request.user)
        serializer = RecorrenciaSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if obj.data_fim is not None:
            obj.ocorrencias.filter(confirmada_em__isnull=True, vencimento__gt=obj.data_fim).delete()
        if not obj.ativa:
            obj.ocorrencias.filter(confirmada_em__isnull=True, vencimento__gte=timezone.localdate()).delete()
        return Response(serializer.data)

    def delete(self, request, pk=None):
        obj = get_object_or_404(Recorrencia, pk=pk, usuario=request.user)
        obj.ativa = False
        obj.save(update_fields=['ativa'])
        obj.ocorrencias.filter(confirmada_em__isnull=True, vencimento__gte=timezone.localdate()).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OcorrenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            inicio = date.fromisoformat(request.query_params['inicio'])
            fim = date.fromisoformat(request.query_params['fim'])
        except (ValueError, KeyError):
            return Response({'detail': 'Informe inicio e fim em AAAA-MM-DD.'}, status=400)
        if fim < inicio or (fim - inicio).days > 366:
            return Response({'detail': 'Período inválido (máximo de 366 dias).'}, status=400)
        # Nunca elimina ocorrências anteriores: pagamentos e histórico são preservados.
        for recorrencia in Recorrencia.objects.filter(
            usuario=request.user, ativa=True, primeiro_vencimento__lte=fim
        ):
            for dia in vencimentos(recorrencia, inicio, fim):
                OcorrenciaRecorrente.objects.get_or_create(recorrencia=recorrencia, vencimento=dia)
        qs = OcorrenciaRecorrente.objects.select_related('recorrencia').filter(
            recorrencia__usuario=request.user, vencimento__gte=inicio, vencimento__lte=fim
        )
        return Response(OcorrenciaSerializer(qs, many=True).data)


class ConfirmarOcorrenciaView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        ocorrencia = get_object_or_404(
            OcorrenciaRecorrente.objects.select_for_update().select_related('recorrencia'),
            pk=pk, recorrencia__usuario=request.user,
        )
        if ocorrencia.confirmada_em:
            return Response(OcorrenciaSerializer(ocorrencia).data)
        recorrencia = ocorrencia.recorrencia
        data_hora = timezone.make_aware(datetime.combine(ocorrencia.vencimento, time(12, 0)))
        lancamento = Transacao.objects.create(
            usuario=request.user, titulo=recorrencia.titulo,
            categoria=recorrencia.categoria, tipo=recorrencia.tipo,
            valor=recorrencia.valor, data=data_hora,
        )
        ocorrencia.transacao = lancamento
        ocorrencia.confirmada_em = timezone.now()
        ocorrencia.save(update_fields=['transacao', 'confirmada_em'])
        return Response(OcorrenciaSerializer(ocorrencia).data)
