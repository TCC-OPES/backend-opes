from django.db import models

from .familia import Familia
from .user import User


class MembroFamilia(models.Model):

    ROLES = (
        ('admin', 'Administrador'),
        ('membro', 'Membro'),
        ('dependente', 'Dependente'),
    )

    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='membros'
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    papel = models.CharField(
        max_length=20,
        choices=ROLES,
        default='membro'
    )

    data_entrada = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Membro da Família"
        verbose_name_plural = "Membros da Família"

    def __str__(self):
        return f"{self.usuario} - {self.familia}"