from rest_framework import serializers
from core.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='user.name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'cpf', 'telefone']