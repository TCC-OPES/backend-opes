import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


def normalizar_membros_e_criadores(apps, schema_editor):
    Familia = apps.get_model('core', 'Familia')
    Membro = apps.get_model('core', 'MembroFamilia')
    vistos = set()
    duplicados = []
    for membro in Membro.objects.order_by('id').iterator():
        chave = (membro.familia_id, membro.usuario_id)
        if chave in vistos:
            duplicados.append(membro.pk)
        else:
            vistos.add(chave)
    if duplicados:
        Membro.objects.filter(pk__in=duplicados).delete()
    for familia in Familia.objects.all().iterator():
        membro, criado = Membro.objects.get_or_create(
            familia_id=familia.pk, usuario_id=familia.criador_id,
            defaults={'papel': 'admin'},
        )
        if not criado and membro.papel != 'admin':
            membro.papel = 'admin'
            membro.save(update_fields=['papel'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_cartao_dia_fechamento'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(normalizar_membros_e_criadores, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='membrofamilia',
            constraint=models.UniqueConstraint(
                fields=('familia', 'usuario'), name='familia_usuario_unico'
            ),
        ),
        migrations.CreateModel(
            name='ConviteFamilia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('papel', models.CharField(
                    choices=[('membro', 'Membro'), ('dependente', 'Dependente')],
                    default='membro', max_length=20,
                )),
                ('status', models.CharField(
                    choices=[
                        ('pendente', 'Pendente'), ('aceito', 'Aceito'),
                        ('recusado', 'Recusado'), ('cancelado', 'Cancelado'),
                    ], default='pendente', max_length=12,
                )),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('respondido_em', models.DateTimeField(blank=True, null=True)),
                ('convidado_por', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='convites_familia_enviados', to=settings.AUTH_USER_MODEL,
                )),
                ('familia', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='convites',
                    to='core.familia',
                )),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='convites_familia', to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['-criado_em']},
        ),
        migrations.AddConstraint(
            model_name='convitefamilia',
            constraint=models.UniqueConstraint(
                fields=('familia', 'usuario'),
                condition=Q(status='pendente'),
                name='convite_familia_pendente_unico',
            ),
        ),
    ]
