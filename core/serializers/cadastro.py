from rest_framework import serializers
from django.db import transaction
from core.models import User, Usuario


class CadastroSerializer(serializers.Serializer):
    nome = serializers.CharField()
    email = serializers.EmailField()
    cpf = serializers.CharField(max_length=11)
    telefone = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def validate_cpf(self, value):
        if Usuario.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("CPF já cadastrado.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['nome']
        )

        usuario = Usuario.objects.create(
            user=user,
            cpf=validated_data['cpf'],
            telefone=validated_data['telefone']
        )

        return usuario