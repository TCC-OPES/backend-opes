from calendar import monthrange
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Investimento, Transacao
from core.models.recorrencia import Recorrencia, OcorrenciaRecorrente
from core.views.recorrencia import vencimentos


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoje = timezone.localdate()
        transacoes = Transacao.objects.filter(usuario=request.user)
        receitas = transacoes.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        despesas = transacoes.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        investido = Investimento.objects.filter(usuario=request.user).aggregate(total=Sum('valor_investido'))['total'] or Decimal('0')
        serie = []
        for indice in range(5, -1, -1):
            total_meses = hoje.year * 12 + hoje.month - 1 - indice
            ano, mes0 = divmod(total_meses, 12)
            inicio = date(ano, mes0 + 1, 1)
            fim = date(ano, mes0 + 1, monthrange(ano, mes0 + 1)[1])
            movimentacoes = transacoes.filter(data__date__gte=inicio, data__date__lte=fim)
            entrada = movimentacoes.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or Decimal('0')
            saida = movimentacoes.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or Decimal('0')
            serie.append({
                'mes': inicio.strftime('%m/%Y'),
                'receitas': entrada,
                'despesas': saida,
                'resultado': entrada - saida,
            })
        segunda = hoje - timedelta(days=hoje.weekday())
        gastos = []
        for indice, dia_nome in enumerate(('Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom')):
            dia = segunda + timedelta(days=indice)
            total = transacoes.filter(tipo='despesa', data__date=dia).aggregate(total=Sum('valor'))['total'] or Decimal('0')
            gastos.append({'dia': dia_nome, 'valor': total})
        fim_previsao = hoje + timedelta(days=30)
        proximas = []
        for recorrencia in Recorrencia.objects.filter(usuario=request.user, ativa=True, primeiro_vencimento__lte=fim_previsao):
            for dia in vencimentos(recorrencia, hoje, fim_previsao):
                if OcorrenciaRecorrente.objects.filter(recorrencia=recorrencia, vencimento=dia, confirmada_em__isnull=False).exists():
                    continue
                proximas.append({
                    'id': recorrencia.id, 'titulo': recorrencia.titulo,
                    'categoria': recorrencia.categoria, 'tipo': recorrencia.tipo,
                    'valor': recorrencia.valor, 'vencimento': dia.isoformat()
                })
        proximas.sort(key=lambda item: (item['vencimento'], item['id']))
        return Response({
            'resumo': {
                'resultado_registrado': receitas - despesas,
                'receitas': receitas,
                'despesas': despesas,
                'total_transacoes': transacoes.count(),
                'total_investido': investido,
            },
            'serie_mensal': serie,
            'gastos_semanais': gastos,
            'proximas': proximas[:5],
            'observacao': 'Resultado dos lançamentos cadastrados, não saldo bancário.',
        })
