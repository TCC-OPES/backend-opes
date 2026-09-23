from django.db import models
from .user import User


class Transacao(models.Model):
    TIPO_CHOICES = (
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transacoes'
    )
    titulo = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    data = models.DateTimeField()

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"