# Generated by Django 3.2.6 on 2021-10-29 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0016_alter_calculo_densidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculo',
            name='medicion',
            field=models.FloatField(blank=True, default=0, max_length=7, null=True, verbose_name='Medición'),
        ),
    ]
