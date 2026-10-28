from rest_framework import serializers
from core.models import MetaFinanceira


class MetaFinanceiraSerializer(serializers.ModelSerializer):

    progresso = serializers.ReadOnlyField()

    def validate_valor_objetivo(self, value):
        if value <= 0:
            raise serializers.ValidationError('O objetivo deve ser maior que zero.')
        return value

    def validate_valor_atual(self, value):
        if value < 0:
            raise serializers.ValidationError('O valor registrado não pode ser negativo.')
        return value

    class Meta:
        model = MetaFinanceira
        fields = '__all__'
        read_only_fields = ['usuario']