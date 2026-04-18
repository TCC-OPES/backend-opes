from rest_framework import serializers
from core.models import Usuario
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    cpf = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            usuario = Usuario.objects.select_related('user').get(cpf=data['cpf'])
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("CPF ou senha inválidos")

        user = authenticate(
            username=usuario.user.email,  
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError("CPF ou senha inválidos")

        data['user'] = user
        return data