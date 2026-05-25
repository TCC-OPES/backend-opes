from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.models import MetaFinanceira
from core.serializers import MetaFinanceiraSerializer


class MetaFinanceiraView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        metas = MetaFinanceira.objects.filter(
            usuario=request.user
        )

        serializer = MetaFinanceiraSerializer(
            metas,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = MetaFinanceiraSerializer(
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