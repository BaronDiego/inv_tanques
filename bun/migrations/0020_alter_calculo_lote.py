# Generated by Django 3.2.6 on 2021-12-23 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0019_tanque_terminal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculo',
            name='lote',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lote', to='bun.lote', verbose_name='Referencia/Lote'),
        ),
    ]
