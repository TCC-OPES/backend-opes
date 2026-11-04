from django.db import models

from .familia import Familia
from .user import User


class ConviteFamilia(models.Model):
    PAPEL_CHOICES = (
        ('admin', 'Administrador'),
        ('membro', 'Membro'),
        ('dependente', 'Dependente'),
    )

    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
        ('cancelado', 'Cancelado'),
    )

    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='convites'
    )
    convidado = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='convites_recebidos'
    )
    convidado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='convites_enviados'
    )
    papel = models.CharField(
        max_length=20,
        choices=PAPEL_CHOICES,
        default='membro'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Convite da Família'
        verbose_name_plural = 'Convites da Família'

    def __str__(self):
        return f'{self.convidado.email} -> {self.familia.nome}'
