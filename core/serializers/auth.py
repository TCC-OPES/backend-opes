from rest_framework import serializers
from core.models import User
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    cpf = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        cpf = data.get('cpf')
        password = data.get('password')

        if cpf and password:
            # Como o USERNAME_FIELD do seu User customizado agora é o CPF, 
            # o Django espera o CPF no argumento 'username'
            user = authenticate(username=cpf, password=password)

            if not user:
                raise serializers.ValidationError("CPF ou senha inválidos.")
            
            if not user.is_active:
                raise serializers.ValidationError("Este usuário está inativo.")
        else:
            raise serializers.ValidationError("É necessário fornecer CPF e senha.")

        data['user'] = user
        return data