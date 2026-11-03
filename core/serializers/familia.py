from rest_framework import serializers
from core.models import Familia, MembroFamilia, DespesaCompartilhada, ConviteFamilia


class MembroFamiliaSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.name', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)

    class Meta:
        model = MembroFamilia
        fields = ['id', 'usuario', 'nome', 'email', 'papel', 'data_entrada']
        read_only_fields = fields


class DespesaCompartilhadaSerializer(serializers.ModelSerializer):
    pago_por_nome = serializers.CharField(source='pago_por.name', read_only=True)

    class Meta:
        model = DespesaCompartilhada
        fields = ['id', 'familia', 'titulo', 'categoria', 'valor', 'pago_por',
                  'pago_por_nome', 'data']
        read_only_fields = fields


class FamiliaSerializer(serializers.ModelSerializer):
    membros = MembroFamiliaSerializer(many=True, read_only=True)
    despesas = DespesaCompartilhadaSerializer(many=True, read_only=True)

    class Meta:
        model = Familia
        fields = ['id', 'nome', 'criador', 'criado_em', 'membros', 'despesas']
        read_only_fields = ['criador', 'criado_em', 'membros', 'despesas']


class ConviteFamiliaSerializer(serializers.ModelSerializer):
    familia_nome = serializers.CharField(source='familia.nome', read_only=True)
    usuario_nome = serializers.CharField(source='usuario.name', read_only=True)
    convidado_por_nome = serializers.CharField(
        source='convidado_por.name', read_only=True, allow_null=True
    )

    class Meta:
        model = ConviteFamilia
        fields = ['id', 'familia', 'familia_nome', 'usuario_nome', 'convidado_por_nome',
                  'papel', 'status', 'criado_em', 'respondido_em']
        read_only_fields = fields


class EnviarConviteFamiliaSerializer(serializers.Serializer):
    email = serializers.EmailField()
    papel = serializers.ChoiceField(choices=['membro', 'dependente'], default='membro')
