from rest_framework import serializers

from core.models import Cartao


class CartaoSerializer(serializers.ModelSerializer):
    vencimento = serializers.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        format='%d/%m/%Y'
    )

    class Meta:
        model = Cartao
        fields = '__all__'
        read_only_fields = ['usuario']
