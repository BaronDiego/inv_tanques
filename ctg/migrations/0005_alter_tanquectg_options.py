# Generated by Django 4.0.2 on 2022-02-18 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ctg', '0004_alter_lotectg_producto_alter_lotectg_referencia'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tanquectg',
            options={'ordering': ['bodega']},
        ),
    ]