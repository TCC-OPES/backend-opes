from rest_framework import serializers

from core.models import Cartao


class CartaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cartao
        fields = '__all__'
        read_only_fields = ['usuario']