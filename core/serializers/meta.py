from rest_framework import serializers
from core.models import MetaFinanceira


class MetaFinanceiraSerializer(serializers.ModelSerializer):

    progresso = serializers.ReadOnlyField()

    class Meta:
        model = MetaFinanceira
        fields = '__all__'
        read_only_fields = ['usuario']