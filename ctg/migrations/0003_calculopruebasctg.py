# Generated by Django 4.0.2 on 2022-02-08 14:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ctg', '0002_tanquectg_bodega'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalculoPruebasCtg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('um', models.IntegerField(blank=True, null=True, verbose_name='Usuario que modifica')),
                ('medicion', models.FloatField(blank=True, default=0, max_length=7, null=True, verbose_name='Medición')),
                ('tabla_6d', models.FloatField(blank=True, default=0, max_length=8, null=True)),
                ('tabla_13', models.FloatField(blank=True, default=0, max_length=8, null=True)),
                ('volumen', models.FloatField(blank=True, max_length=8, null=True)),
                ('temperatura_tq', models.FloatField(blank=True, max_length=4, null=True)),
                ('sellos_valvulas', models.CharField(blank=True, max_length=150, verbose_name='Sellos Válvulas')),
                ('sellos_tapas', models.CharField(blank=True, max_length=150)),
                ('densidad', models.FloatField(blank=True, default=0, max_length=8, null=True)),
                ('masa', models.FloatField(blank=True, max_length=8, null=True)),
                ('lote', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ctg.lotectg', verbose_name='Referencia/Lote')),
                ('tanque', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ctg.tanquectg')),
                ('uc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario que Crea')),
            ],
            options={
                'ordering': ['-creado'],
            },
        ),
    ]
