from rest_framework import serializers
from core.models import Cartao


class CartaoSerializer(serializers.ModelSerializer):
    cor = serializers.RegexField(
        regex=r'^#[0-9a-fA-F]{6}$',
        max_length=7,
        required=False,
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

    def validate(self, attrs):
        limite = attrs.get('limite_total', getattr(self.instance, 'limite_total', None))
        utilizado = attrs.get('valor_utilizado', getattr(self.instance, 'valor_utilizado', 0))
        if limite is not None and limite < 0:
            raise serializers.ValidationError({'limite_total': 'O limite não pode ser negativo.'})
        if utilizado is not None and utilizado < 0:
            raise serializers.ValidationError({'valor_utilizado': 'O valor utilizado não pode ser negativo.'})
        if limite is not None and utilizado is not None and utilizado > limite:
            raise serializers.ValidationError({'valor_utilizado': 'O valor utilizado não pode superar o limite total.'})
        return attrs
