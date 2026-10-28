from django.conf import settings
from django.db import models


class Recorrencia(models.Model):
    FREQUENCIAS = [('mensal', 'Mensal'), ('semanal', 'Semanal'), ('anual', 'Anual')]
    TIPOS = [('receita', 'Receita'), ('despesa', 'Despesa')]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recorrencias')
    titulo = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    frequencia = models.CharField(max_length=10, choices=FREQUENCIAS, default='mensal')
    primeiro_vencimento = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    numero_parcelas = models.PositiveSmallIntegerField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['primeiro_vencimento', 'id']

    def __str__(self):
        return self.titulo


class OcorrenciaRecorrente(models.Model):
    recorrencia = models.ForeignKey(Recorrencia, on_delete=models.CASCADE, related_name='ocorrencias')
    vencimento = models.DateField()
    confirmada_em = models.DateTimeField(null=True, blank=True)
    transacao = models.OneToOneField(
        'core.Transacao', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ocorrencia_recorrente',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recorrencia', 'vencimento'], name='unica_ocorrencia_por_vencimento')
        ]
        ordering = ['vencimento', 'id']
