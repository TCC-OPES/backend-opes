from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_recorrencia_numero_parcelas'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartao',
            name='cor',
            field=models.CharField(default='#14372D', max_length=7),
        ),
    ]
