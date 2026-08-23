from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'cpf', 'email', 'name', 'telefone', 'nascimento', 'foto', 'criado_em']
        read_only_fields = ['id', 'email', 'criado_em']
        # Remove os validadores de unicidade automaticos do ModelSerializer
        extra_kwargs = {
            'cpf': {'validators': []},
            'email': {'validators': []},
        }

    def validate_cpf(self, value):
        if not value:
            return value
            
        cpf_limpo = ''.join(filter(str.isdigit, str(value)))
        if len(cpf_limpo) != 11:
            raise serializers.ValidationError("O CPF deve conter exatamente 11 dígitos.")
        
        # Verifica se o CPF ja esta em uso por OUTRO usuario
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(cpf=cpf_limpo).exclude(id=user_id).exists():
            raise serializers.ValidationError("Usuário com este CPF já existe.")
            
        return cpf_limpo

    def validate_telefone(self, value):
        if value:
            return ''.join(filter(str.isdigit, str(value)))
        return value