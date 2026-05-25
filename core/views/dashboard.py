from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Sum
from core.models import Transacao


class DashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        transacoes = Transacao.objects.filter(usuario=request.user)

        receitas = transacoes.filter(tipo='receita').aggregate(total=Sum('valor'))
        despesas = transacoes.filter(tipo='despesa').aggregate(total=Sum('valor'))

        return Response({
            "total_transacoes": transacoes.count(),
            "receitas": receitas["total"] or 0,
            "despesas": despesas["total"] or 0
        })