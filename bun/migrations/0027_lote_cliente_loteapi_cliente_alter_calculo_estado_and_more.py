# Generated by Django 4.0.2 on 2022-04-11 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0026_loteapi_calculoapi'),
    ]

    operations = [
        migrations.AddField(
            model_name='lote',
            name='cliente',
            field=models.CharField(blank=True, default='-', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='loteapi',
            name='cliente',
            field=models.CharField(blank=True, default='-', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='calculo',
            name='estado',
            field=models.CharField(choices=[('F', 'FINAL'), ('I', 'INICIAL'), ('C', 'CONTROL'), ('D', 'DEFINITIVA'), ('ID', 'INICAL DESPACHO'), ('IR', 'INICIAL RECIBO'), ('FD', 'FINAL DESPACHO'), ('FR', 'FINAL RECIBO')], max_length=2),
        ),
        migrations.AlterField(
            model_name='calculoapi',
            name='estado',
            field=models.CharField(choices=[('F', 'FINAL'), ('I', 'INICIAL'), ('C', 'CONTROL'), ('D', 'DEFINITIVA'), ('ID', 'INICAL DESPACHO'), ('IR', 'INICIAL RECIBO'), ('FD', 'FINAL DESPACHO'), ('FR', 'FINAL RECIBO')], max_length=2),
        ),
    ]
