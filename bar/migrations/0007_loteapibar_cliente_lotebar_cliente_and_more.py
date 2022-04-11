# Generated by Django 4.0.2 on 2022-04-11 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bar', '0006_loteapibar_calculoapibar'),
    ]

    operations = [
        migrations.AddField(
            model_name='loteapibar',
            name='cliente',
            field=models.CharField(blank=True, default='-', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='lotebar',
            name='cliente',
            field=models.CharField(blank=True, default='-', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='calculoapibar',
            name='estado',
            field=models.CharField(choices=[('F', 'FINAL'), ('I', 'INICIAL'), ('C', 'CONTROL'), ('D', 'DEFINITIVA'), ('ID', 'INICAL DESPACHO'), ('IR', 'INICIAL RECIBO'), ('FD', 'FINAL DESPACHO'), ('FR', 'FINAL RECIBO')], max_length=2),
        ),
        migrations.AlterField(
            model_name='calculobar',
            name='estado',
            field=models.CharField(choices=[('F', 'FINAL'), ('I', 'INICIAL'), ('C', 'CONTROL'), ('D', 'DEFINITIVA'), ('ID', 'INICAL DESPACHO'), ('IR', 'INICIAL RECIBO'), ('FD', 'FINAL DESPACHO'), ('FR', 'FINAL RECIBO')], max_length=2),
        ),
    ]