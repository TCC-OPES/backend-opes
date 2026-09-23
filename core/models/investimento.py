from django.db import models


class Investimento(models.Model):
    TIPOS = [
        ('renda_fixa', 'Renda Fixa'),
        ('acoes', 'Ações'),
        ('fiis', 'FIIs'),
        ('cripto', 'Criptomoedas'),
        ('outros', 'Outros'),
    ]

    usuario = models.ForeignKey(
        'core.User', 
        on_delete=models.CASCADE, 
        related_name='investimentos'
    )
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='renda_fixa')
    valor_investido = models.DecimalField(max_digits=12, decimal_places=2)
    rentabilidade = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cor = models.CharField(max_length=7, default='#2563EB')  # <-- ADICIONE ESTA LINHA
    data_aplicacao = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - R$ {self.valor_investido}"