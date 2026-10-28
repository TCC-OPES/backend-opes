from rest_framework import serializers
from core.models import Investimento


class InvestimentoSerializer(serializers.ModelSerializer):
    def validate_valor_investido(self, value):
        if value <= 0:
            raise serializers.ValidationError('Informe um valor investido positivo.')
        return value

    class Meta:
        model = Investimento
        fields = ['id', 'nome', 'tipo', 'valor_investido', 'rentabilidade', 'cor', 'data_aplicacao']
        read_only_fields = ['id', 'usuario', 'data_aplicacao']