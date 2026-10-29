from django.db import models
from .user import User


class Transacao(models.Model):
    TIPO_CHOICES = (('receita', 'Receita'), ('despesa', 'Despesa'))
    METODO_CHOICES = (
        ('pix', 'Pix'),
        ('dinheiro', 'Dinheiro'),
        ('debito', 'Cartão de débito'),
        ('credito', 'Cartão de crédito'),
        ('outro', 'Outro / não informado'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacoes')
    titulo = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField()
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_CHOICES, default='outro')
    cartao = models.ForeignKey(
        'core.Cartao',
        on_delete=models.PROTECT,
        related_name='transacoes_credito',
        null=True,
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    def __str__(self):
        return f'{self.titulo} ({self.tipo})'
