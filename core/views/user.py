from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from core.models import Usuario
from core.serializers import UsuarioSerializer


class UserViewSet(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "message": "Usuário criado com sucesso 🚀",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )