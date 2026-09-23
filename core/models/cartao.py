from django.db import models
from .user import User


class Cartao(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cartoes'
    )

    banco = models.CharField(max_length=100)

    nome = models.CharField(max_length=100)

    limite_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    valor_utilizado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    vencimento = models.DateField()

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Cartão"
        verbose_name_plural = "Cartões"

    def __str__(self):
        return f"{self.nome} - {self.banco}"