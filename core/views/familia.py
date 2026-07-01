from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Familia
from core.serializers import FamiliaSerializer


class FamiliaView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        familias = Familia.objects.filter(criador=request.user)
        serializer = FamiliaSerializer(familias, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FamiliaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(criador=request.user)
        return Response(serializer.data)