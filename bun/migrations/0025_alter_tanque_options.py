# Generated by Django 4.0.2 on 2022-02-18 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bun', '0024_alter_tanque_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tanque',
            options={'ordering': ['bodega']},
        ),
    ]