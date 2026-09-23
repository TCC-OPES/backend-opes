from django.conf import settings
from django.db import models


class ConexaoBancaria(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conexoes_bancarias"
    )
    item_id = models.CharField(max_length=255, unique=True)
    instituicao_nome = models.CharField(max_length=255, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.item_id}"


class TransacaoImportada(models.Model):
    conexao = models.ForeignKey(
        ConexaoBancaria, on_delete=models.CASCADE, related_name="transacoes_importadas"
    )
    external_id = models.CharField(max_length=255, unique=True)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateTimeField()
    categoria = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} ({self.valor})"