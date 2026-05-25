from rest_framework import serializers  
from core.models import (
    Familia,
    MembroFamilia,
    DespesaCompartilhada
)


class FamiliaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Familia
        fields = '__all__'


class MembroFamiliaSerializer(serializers.ModelSerializer):

    class Meta:
        model = MembroFamilia
        fields = '__all__'


class DespesaCompartilhadaSerializer(serializers.ModelSerializer):

    class Meta:
        model = DespesaCompartilhada
        fields = '__all__'