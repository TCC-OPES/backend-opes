from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_cartao_cor'),
    ]
    operations = [
        migrations.AddField(
            model_name='transacao',
            name='metodo_pagamento',
            field=models.CharField(
                choices=[
                    ('pix', 'Pix'),
                    ('dinheiro', 'Dinheiro'),
                    ('debito', 'Cartão de débito'),
                    ('credito', 'Cartão de crédito'),
                    ('outro', 'Outro / não informado'),
                ],
                default='outro',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='transacao',
            name='cartao',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='transacoes_credito',
                to='core.cartao',
            ),
        ),
    ]
