from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.models import MetaFinanceira
from core.serializers import MetaFinanceiraSerializer


class MetaFinanceiraView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                meta = MetaFinanceira.objects.get(pk=pk, usuario=request.user)
                serializer = MetaFinanceiraSerializer(meta)
                return Response(serializer.data)
            except MetaFinanceira.DoesNotExist:
                return Response(
                    {'detail': 'Meta não encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        metas = MetaFinanceira.objects.filter(usuario=request.user)
        serializer = MetaFinanceiraSerializer(metas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MetaFinanceiraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def put(self, request, pk=None):
        if not pk:
            return Response(
                {'detail': 'ID não fornecido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            meta = MetaFinanceira.objects.get(pk=pk, usuario=request.user)
        except MetaFinanceira.DoesNotExist:
            return Response(
                {'detail': 'Meta não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MetaFinanceiraSerializer(
            meta,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk=None):
        if not pk:
            return Response(
                {'detail': 'ID não fornecido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            meta = MetaFinanceira.objects.get(pk=pk, usuario=request.user)
            meta.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MetaFinanceira.DoesNotExist:
            return Response(
                {'detail': 'Meta não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )