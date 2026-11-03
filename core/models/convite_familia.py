from django.db import models

from .familia import Familia
from .user import User


class ConviteFamilia(models.Model):
    PENDENTE = 'pendente'
    ACEITO = 'aceito'
    RECUSADO = 'recusado'
    CANCELADO = 'cancelado'
    STATUS = [
        (PENDENTE, 'Pendente'),
        (ACEITO, 'Aceito'),
        (RECUSADO, 'Recusado'),
        (CANCELADO, 'Cancelado'),
    ]

    familia = models.ForeignKey(Familia, on_delete=models.CASCADE, related_name='convites')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='convites_familia')
    convidado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='convites_familia_enviados'
    )
    papel = models.CharField(
        max_length=20, choices=[('membro', 'Membro'), ('dependente', 'Dependente')],
        default='membro',
    )
    status = models.CharField(max_length=12, choices=STATUS, default=PENDENTE)
    criado_em = models.DateTimeField(auto_now_add=True)
    respondido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['familia', 'usuario'],
                condition=models.Q(status='pendente'),
                name='convite_familia_pendente_unico',
            ),
        ]
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.familia_id} - {self.usuario_id} ({self.status})'
