# Generated by Django 3.2.6 on 2021-09-06 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0003_auto_20210906_1108'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lote',
            options={'ordering': ['-creado']},
        ),
    ]
