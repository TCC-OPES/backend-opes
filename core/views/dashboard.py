from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum

# Importe os seus models correspondentes
from core.models import Transacao, Investimento


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user

        # 1. Transações do Usuário
        transacoes = Transacao.objects.filter(usuario=usuario)
        receitas = transacoes.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or 0
        despesas = transacoes.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or 0

        # 2. Saldos de Carteiras e Investimentos
        total_carteiras = Carteira.objects.filter(usuario=usuario).aggregate(total=Sum('saldo'))['total'] or 0
        total_investido = Investimento.objects.filter(usuario=usuario).aggregate(total=Sum('valor_investido'))['total'] or 0

        # Saldo Total (Patrimônio) = Saldo das contas + Total Investido
        saldo_total = (total_carteiras + total_investido) - despesas

        # 3. Próximas Transações (Ex: últimas 5)
        proximas_transacoes = transacoes.order_by('-data')[:5].values(
            'id', 'descricao', 'valor', 'tipo', 'data'
        )

        # 4. Dados Mockados/Calculados para o Gráfico de Evolução Patrimonial
        # Ajuste com a sua lógica real de histórico de meses
        dados_grafico = [
            {"mes": "Out", "valor": saldo_total * 0.8},
            {"mes": "Nov", "valor": saldo_total * 0.85},
            {"mes": "Dez", "valor": saldo_total * 0.9},
            {"mes": "Jan", "valor": saldo_total * 0.95},
            {"mes": "Fev", "valor": saldo_total},
        ]

        return Response({
            "resumo": {
                "saldo_total": saldo_total,
                "total_investido": total_investido,
                "receitas": receitas,
                "despesas": despesas,
                "total_transacoes": transacoes.count()
            },
            "graficos": {
                "evolucao_patrimonial": dados_grafico
            },
            "proximas": list(proximas_transacoes)
        })