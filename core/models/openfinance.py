from django.conf import settings
from django.db import models


class ConexaoBancaria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conexoes_bancarias',
    )
    item_id = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario_id} - {self.item_id}'


class TransacaoImportada(models.Model):
    conexao = models.ForeignKey(
        ConexaoBancaria,
        on_delete=models.CASCADE,
        related_name='transacoes',
    )
    conta_id = models.CharField(max_length=64)
    id_externo = models.CharField(max_length=64, unique=True)
    descricao = models.CharField(max_length=255, blank=True)
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    tipo = models.CharField(max_length=10, blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    data = models.DateField()

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f'{self.data} {self.descricao} {self.valor}'