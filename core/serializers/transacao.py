from rest_framework import serializers
from core.models import Transacao


class TransacaoSerializer(serializers.ModelSerializer):
    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('Informe um valor positivo.')
        return value

    def validate(self, attrs):
        usuario = self.context['request'].user
        tipo = attrs.get('tipo', getattr(self.instance, 'tipo', None))
        metodo = attrs.get('metodo_pagamento', getattr(self.instance, 'metodo_pagamento', 'outro'))
        cartao = attrs.get('cartao', getattr(self.instance, 'cartao', None))

        if cartao is not None and cartao.usuario_id != usuario.pk:
            raise serializers.ValidationError({'cartao': 'Este cartão não pertence ao usuário.'})

        if tipo == 'despesa' and metodo == 'credito':
            if cartao is None:
                raise serializers.ValidationError({'cartao': 'Selecione o cartão de crédito utilizado.'})
        elif cartao is not None:
            raise serializers.ValidationError({'cartao': 'O cartão só deve ser informado em despesas no crédito.'})
        return attrs

    class Meta:
        model = Transacao
        fields = '__all__'
        read_only_fields = ['usuario']
