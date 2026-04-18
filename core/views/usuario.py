from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from core.serializers import CadastroSerializer, UsuarioSerializer


class CadastroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CadastroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = serializer.save()

        return Response(
            {
                "message": "Usuário cadastrado com sucesso",
            },
            status=status.HTTP_201_CREATED
        )