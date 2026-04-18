from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.serializers import UsuarioSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user.perfil
        return Response({
            "data": UsuarioSerializer(usuario).data
        })