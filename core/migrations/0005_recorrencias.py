from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_investimento_cor'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recorrencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('categoria', models.CharField(max_length=100)),
                ('tipo', models.CharField(choices=[('receita', 'Receita'), ('despesa', 'Despesa')], max_length=20)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=12)),
                ('frequencia', models.CharField(choices=[('mensal', 'Mensal'), ('semanal', 'Semanal'), ('anual', 'Anual')], default='mensal', max_length=10)),
                ('primeiro_vencimento', models.DateField()),
                ('data_fim', models.DateField(blank=True, null=True)),
                ('ativa', models.BooleanField(default=True)),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recorrencias', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['primeiro_vencimento', 'id']},
        ),
        migrations.CreateModel(
            name='OcorrenciaRecorrente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vencimento', models.DateField()),
                ('confirmada_em', models.DateTimeField(blank=True, null=True)),
                ('recorrencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ocorrencias', to='core.recorrencia')),
                ('transacao', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ocorrencia_recorrente', to='core.transacao')),
            ],
            options={'ordering': ['vencimento', 'id']},
        ),
        migrations.AddConstraint(
            model_name='ocorrenciarecorrente',
            constraint=models.UniqueConstraint(fields=('recorrencia', 'vencimento'), name='unica_ocorrencia_por_vencimento'),
        ),
    ]
