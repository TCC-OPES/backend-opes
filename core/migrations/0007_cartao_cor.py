from django.db import migrations, models


CORES_INICIAIS = (
    '#14372D',  # Verde OPES
    '#295B83',  # Azul
    '#6C4A73',  # Roxo
    '#935A39',  # Terracota
    '#374151',  # Grafite
    '#7D4655',  # Vinho
)


def colorir_cartoes_existentes(apps, schema_editor):
    Cartao = apps.get_model('core', 'Cartao')
    for indice, cartao in enumerate(Cartao.objects.order_by('usuario_id', 'id').iterator()):
        cartao.cor = CORES_INICIAIS[indice % len(CORES_INICIAIS)]
        cartao.save(update_fields=['cor'])


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
        migrations.RunPython(colorir_cartoes_existentes, migrations.RunPython.noop),
    ]
