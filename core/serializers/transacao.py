from rest_framework import serializers
from core.models import Transacao


class TransacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transacao
        fields = '__all__'
        read_only_fields = ['usuario']