# Generated by Django 3.2.6 on 2021-09-23 21:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0007_calculo_estado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='calculo',
            old_name='centimetros',
            new_name='medicion',
        ),
        migrations.RenameField(
            model_name='lote',
            old_name='referncia',
            new_name='referencia',
        ),
        migrations.RemoveField(
            model_name='aforotanque',
            name='centimetros',
        ),
        migrations.RemoveField(
            model_name='aforotanque',
            name='metros',
        ),
        migrations.RemoveField(
            model_name='calculo',
            name='metros',
        ),
        migrations.RemoveField(
            model_name='calculo',
            name='milimetros',
        ),
    ]
