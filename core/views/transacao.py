from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from core.models import Transacao
from core.serializers import TransacaoSerializer
from openfinance.models import TransacaoImportada


class TransacaoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tipo = request.query_params.get('tipo')
        
        
        transacoes = Transacao.objects.filter(usuario=request.user)
        importadas = TransacaoImportada.objects.filter(conexao__user=request.user)
        
        if tipo and tipo != 'todas':
            transacoes = transacoes.filter(tipo=tipo)
            importadas = importadas.filter(tipo=tipo)
            
        serializer = TransacaoSerializer(
            transacoes,
            many=True
        )
        bancarias = [
            {
                'id': f'bank-{t.pk}',
                'titulo': t.descricao,
                'categoria': t.categoria or 'Sem categoria',
                'tipo': t.tipo,
                'valor': t.valor,
                'data': t.data.isoformat(),
                'origem': 'banco',
                'instituicao_nome': t.conexao.instituicao_nome,
            }
            for t in importadas.select_related('conexao')
        ]
        resultado = [{**item, 'origem': 'manual'} for item in serializer.data] + bancarias
        resultado.sort(key=lambda item: parse_datetime(item['data']).timestamp(), reverse=True)
        return Response(resultado)

    def post(self, request):
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
