from rest_framework import serializers

from core.models import Cartao


class CartaoSerializer(serializers.ModelSerializer):
    cor = serializers.RegexField(
        regex=r'^#[0-9a-fA-F]{6}
    vencimento = serializers.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        format='%d/%m/%Y'
    )

    class Meta:
        model = Cartao
        fields = '__all__'
        read_only_fields = ['usuario']
,
        max_length=7,
        required=False,
        default='#14372D',
        error_messages={'invalid': 'Informe uma cor hexadecimal válida (#RRGGBB).'},
    )
    vencimento = serializers.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        format='%d/%m/%Y'
    )

    class Meta:
        model = Cartao
        fields = '__all__'
        read_only_fields = ['usuario']
