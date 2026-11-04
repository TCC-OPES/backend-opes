from rest_framework import serializers
from core.models import Familia, MembroFamilia, DespesaCompartilhada, ConviteFamilia


class DespesaCompartilhadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DespesaCompartilhada
        fields = '__all__'


class MembroFamiliaSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = MembroFamilia
        fields = ['id', 'familia', 'usuario', 'usuario_nome', 'email', 'papel', 'data_entrada']

    def get_usuario_nome(self, obj):
        return obj.usuario.name or obj.usuario.email or 'Membro'

    def get_email(self, obj):
        return obj.usuario.email


class FamiliaSerializer(serializers.ModelSerializer):
    membros = serializers.SerializerMethodField()
    despesas = serializers.SerializerMethodField()

    class Meta:
        model = Familia
        fields = ['id', 'nome', 'criador', 'criado_em', 'membros', 'despesas']
        read_only_fields = ['criador', 'criado_em']

    def get_membros(self, obj):
        return MembroFamiliaSerializer(obj.membros.all(), many=True).data

    def get_despesas(self, obj):
        return DespesaCompartilhadaSerializer(obj.despesas.all(), many=True).data


class ConviteFamiliaSerializer(serializers.ModelSerializer):
    familia_nome = serializers.SerializerMethodField()
    convidado_por_nome = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    usuario_nome = serializers.SerializerMethodField()

    class Meta:
        model = ConviteFamilia
        fields = [
            'id', 'familia', 'familia_nome', 'convidado', 'usuario_email', 'usuario_nome',
            'convidado_por', 'convidado_por_nome', 'papel', 'status', 'criado_em'
        ]

    def get_familia_nome(self, obj):
        return obj.familia.nome

    def get_convidado_por_nome(self, obj):
        return obj.convidado_por.name or obj.convidado_por.email or 'Administrador'

    def get_usuario_email(self, obj):
        return obj.convidado.email

    def get_usuario_nome(self, obj):
        return obj.convidado.name or obj.convidado.email or 'Usuário'
