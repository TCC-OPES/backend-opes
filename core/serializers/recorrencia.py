from calendar import monthrange
from rest_framework import serializers

from core.models.recorrencia import Recorrencia, OcorrenciaRecorrente


class RecorrenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recorrencia
        fields = ['id', 'titulo', 'categoria', 'tipo', 'valor', 'frequencia',
                  'primeiro_vencimento', 'data_fim', 'numero_parcelas', 'ativa', 'criada_em']
        read_only_fields = ['id', 'criada_em']

    def create(self, validated_data):
        validated_data['ativa'] = True
        return super().create(validated_data)

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError('O valor deve ser maior que zero.')
        return value

    def validate_numero_parcelas(self, value):
        if value is not None and not 1 <= value <= 360:
            raise serializers.ValidationError('Informe entre 1 e 360 parcelas.')
        return value

    def validate(self, attrs):
        inicio = attrs.get('primeiro_vencimento', getattr(self.instance, 'primeiro_vencimento', None))
        frequencia = attrs.get('frequencia', getattr(self.instance, 'frequencia', 'mensal'))
        parcelas = attrs.get('numero_parcelas', getattr(self.instance, 'numero_parcelas', None))
        fim = attrs.get('data_fim', getattr(self.instance, 'data_fim', None))
        if parcelas is not None:
            if frequencia != 'mensal':
                raise serializers.ValidationError({'numero_parcelas': 'Parcelamento disponível apenas para recorrências mensais.'})
            if inicio:
                indice = inicio.year * 12 + inicio.month - 1 + parcelas - 1
                ano, mes = divmod(indice, 12)
                from datetime import date
                calculado = date(ano, mes + 1, min(inicio.day, monthrange(ano, mes + 1)[1]))
                if 'data_fim' in attrs and attrs['data_fim'] not in (None, calculado):
                    raise serializers.ValidationError({'data_fim': 'O último vencimento é calculado a partir das parcelas.'})
                attrs['data_fim'] = calculado
                fim = calculado
        if fim and inicio and fim < inicio:
            raise serializers.ValidationError({'data_fim': 'O término deve ser após o primeiro vencimento.'})
        campos_protegidos = ('frequencia', 'primeiro_vencimento', 'tipo', 'valor', 'titulo', 'categoria', 'numero_parcelas')
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
    numero_parcelas = serializers.IntegerField(source='recorrencia.numero_parcelas', read_only=True)
    parcela_atual = serializers.SerializerMethodField()

    class Meta:
        model = OcorrenciaRecorrente
        fields = ['id', 'recorrencia', 'titulo', 'categoria', 'tipo', 'valor',
                  'vencimento', 'confirmada_em', 'transacao', 'status', 'numero_parcelas', 'parcela_atual']
        read_only_fields = fields

    def get_parcela_atual(self, obj):
        recorrencia = obj.recorrencia
        if not recorrencia.numero_parcelas:
            return None
        base = recorrencia.primeiro_vencimento
        return (obj.vencimento.year - base.year) * 12 + obj.vencimento.month - base.month + 1

    def get_status(self, obj):
        from django.utils import timezone
        if obj.confirmada_em:
            return 'confirmada'
        return 'atrasada' if obj.vencimento < timezone.localdate() else 'pendente'
