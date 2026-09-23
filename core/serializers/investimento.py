from rest_framework import serializers
from core.models import Investimento


class InvestimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investimento
        fields = ['id', 'nome', 'tipo', 'valor_investido', 'rentabilidade', 'cor', 'data_aplicacao']  # <-- 'cor' DEVE ESTAR AQUI
        read_only_fields = ['id', 'usuario', 'data_aplicacao']