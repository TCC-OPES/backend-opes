from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_transacao_metodo_cartao'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartao',
            name='dia_fechamento',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
