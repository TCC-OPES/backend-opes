from rest_framework import serializers

from core.models.openfinance import ConexaoBancaria, TransacaoImportada


class ConexaoBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConexaoBancaria
        fields = ['id', 'item_id', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class TransacaoImportadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransacaoImportada
        fields = [
            'id',
            'conta_id',
            'id_externo',
            'descricao',
            'valor',
            'tipo',
            'categoria',
            'data',
        ]
        read_only_fields = fields