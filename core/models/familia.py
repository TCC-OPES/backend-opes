from django.db import models

from .user import User


class Familia(models.Model):

    nome = models.CharField(
        max_length=255
    )

    criador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='familias_criadas'
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )