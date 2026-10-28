from rest_framework import serializers
from core.models import Transacao


class TransacaoSerializer(serializers.ModelSerializer):

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('Informe um valor positivo.')
        return value

    class Meta:
        model = Transacao
        fields = '__all__'
        read_only_fields = ['usuario']