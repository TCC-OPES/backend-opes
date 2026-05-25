from django.db import models

from .user import User


class MetaFinanceira(models.Model):

    CATEGORIAS = (
        ('lazer', 'Lazer'),
        ('veiculo', 'Veículo'),
        ('seguranca', 'Segurança'),
        ('educacao', 'Educação'),
        ('moradia', 'Moradia'),
        ('saude', 'Saúde'),
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='metas'
    )

    titulo = models.CharField(
        max_length=255
    )

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS
    )

    descricao = models.TextField()

    valor_objetivo = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    valor_atual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    valor_mensal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    data_limite = models.DateField()

    criada_em = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def progresso(self):
        if self.valor_objetivo == 0:
            return 0

        return round(
            (self.valor_atual / self.valor_objetivo) * 100,
            1
        )