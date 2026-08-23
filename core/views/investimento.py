from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import Investimento
from core.serializers import InvestimentoSerializer

class InvestimentoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                investimento = Investimento.objects.get(pk=pk, usuario=request.user)
                serializer = InvestimentoSerializer(investimento)
                return Response(serializer.data)
            except Investimento.DoesNotExist:
                return Response({'detail': 'Não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        investimentos = Investimento.objects.filter(usuario=request.user)
        serializer = InvestimentoSerializer(investimentos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InvestimentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            investimento = Investimento.objects.get(pk=pk, usuario=request.user)
            investimento.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Investimento.DoesNotExist:
            return Response({'detail': 'Não encontrado.'}, status=status.HTTP_404_NOT_FOUND)