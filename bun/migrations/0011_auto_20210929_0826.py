# Generated by Django 3.2.6 on 2021-09-29 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0010_auto_20210927_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculo',
            name='sellos_tapas',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='calculo',
            name='sellos_valvulas',
            field=models.CharField(blank=True, max_length=150, verbose_name='Sellos Válvulas'),
        ),
    ]
