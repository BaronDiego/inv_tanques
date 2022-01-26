# Generated by Django 3.2.6 on 2021-09-06 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0002_auto_20210906_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculo',
            name='densidad',
            field=models.FloatField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='calculo',
            name='lote',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bun.lote'),
        ),
        migrations.AddField(
            model_name='calculo',
            name='masa',
            field=models.FloatField(blank=True, max_length=8, null=True),
        ),
    ]
