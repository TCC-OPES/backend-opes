from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0005_recorrencias')]

    operations = [
        migrations.AddField(
            model_name='recorrencia',
            name='numero_parcelas',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
