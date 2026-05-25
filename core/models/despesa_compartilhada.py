from django.db import models

from .familia import Familia
from .user import User


class DespesaCompartilhada(models.Model):

    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='despesas'
    )

    titulo = models.CharField(
        max_length=255
    )

    categoria = models.CharField(
        max_length=100
    )

    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    pago_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    data = models.DateField()

    class Meta:
        verbose_name = "Despesa Compartilhada"
        verbose_name_plural = "Despesas Compartilhadas"

    def __str__(self):
        return self.titulo