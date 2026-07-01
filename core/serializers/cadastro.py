from rest_framework import serializers
from core.models import User
from django.contrib.auth.hashers import make_password

class CadastroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'cpf', 'password', 'password_confirm']

    def validate_cpf(self, value):
        cpf_limpo = ''.join(filter(str.isdigit, value))
        
        if len(cpf_limpo) != 11:
            raise serializers.ValidationError("O CPF deve conter exatamente 11 dígitos.")
            
        if User.objects.filter(cpf=cpf_limpo).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
            
        return cpf_limpo

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "As senhas não conferem."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)