from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser 

from core.serializers import CadastroSerializer, UsuarioSerializer


# 1. VIEW DE CADASTRO (Garante que a URL de cadastro volte a funcionar)
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


# 2. VIEW DA FOTO DE PERFIL
class AtualizarFotoPerfilView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request): 
        usuario = request.user

        if 'foto' in request.FILES:
            usuario.foto = request.FILES['foto']
            usuario.save()

            foto_url = request.build_absolute_uri(usuario.foto.url)

            return Response(
                {
                    "message": "Foto de perfil atualizada com sucesso",
                    "foto_url": foto_url
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Nenhuma imagem foi enviada"}, 
            status=status.HTTP_400_BAD_REQUEST
        )