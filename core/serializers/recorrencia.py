from rest_framework import serializers

from core.models.recorrencia import Recorrencia, OcorrenciaRecorrente


class RecorrenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recorrencia
        fields = ['id', 'titulo', 'categoria', 'tipo', 'valor', 'frequencia',
                  'primeiro_vencimento', 'data_fim', 'ativa', 'criada_em']
        read_only_fields = ['id', 'criada_em']

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('O valor deve ser maior que zero.')
        return value

    def validate(self, attrs):
        inicio = attrs.get('primeiro_vencimento', getattr(self.instance, 'primeiro_vencimento', None))
        fim = attrs.get('data_fim', getattr(self.instance, 'data_fim', None))
        if fim and inicio and fim < inicio:
            raise serializers.ValidationError({'data_fim': 'O término deve ser após o primeiro vencimento.'})
        campos_protegidos = ('frequencia', 'primeiro_vencimento', 'tipo', 'valor', 'titulo', 'categoria')
        if self.instance and self.instance.ocorrencias.exists():
            alterados = [campo for campo in campos_protegidos
                         if campo in attrs and attrs[campo] != getattr(self.instance, campo)]
            if alterados:
                raise serializers.ValidationError(
                    'Não é possível alterar dados financeiros após gerar vencimentos. '
                    'Encerre esta recorrência e crie outra.'
                )
        return attrs


class OcorrenciaSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(source='recorrencia.titulo', read_only=True)
    categoria = serializers.CharField(source='recorrencia.categoria', read_only=True)
    tipo = serializers.CharField(source='recorrencia.tipo', read_only=True)
    valor = serializers.DecimalField(source='recorrencia.valor', max_digits=12, decimal_places=2, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = OcorrenciaRecorrente
        fields = ['id', 'recorrencia', 'titulo', 'categoria', 'tipo', 'valor',
                  'vencimento', 'confirmada_em', 'transacao', 'status']
        read_only_fields = fields

    def get_status(self, obj):
        from django.utils import timezone
        if obj.confirmada_em:
            return 'confirmada'
        return 'atrasada' if obj.vencimento < timezone.localdate() else 'pendente'
