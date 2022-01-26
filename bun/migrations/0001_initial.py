# Generated by Django 3.2.6 on 2021-08-30 13:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tanque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=50, unique=True)),
                ('tipo', models.CharField(max_length=150)),
                ('diametro', models.FloatField(max_length=6)),
                ('altura_cilindro', models.FloatField(max_length=6)),
                ('altura_medicion', models.FloatField(max_length=6)),
                ('fecha_aforo', models.DateField()),
                ('norma', models.CharField(max_length=150)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('um', models.IntegerField(blank=True, null=True, verbose_name='Usuario que modifica')),
                ('uc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario que Crea')),
            ],
        ),
        migrations.CreateModel(
            name='Calculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metros', models.FloatField(blank=True, max_length=7, null=True)),
                ('centimetros', models.FloatField(blank=True, max_length=7, null=True)),
                ('milimetros', models.FloatField(blank=True, max_length=7, null=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('um', models.IntegerField(blank=True, null=True, verbose_name='Usuario que modifica')),
                ('volumen', models.FloatField(blank=True, max_length=8, null=True)),
                ('temperatura_tq', models.FloatField(blank=True, max_length=4, null=True)),
                ('temperatura_ref', models.FloatField(blank=True, max_length=4, null=True)),
                ('densidad_ref', models.FloatField(blank=True, max_length=6, null=True)),
                ('factor_correccion', models.FloatField(blank=True, max_length=6, null=True)),
                ('tanque', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bun.tanque')),
                ('uc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario que Crea')),
            ],
            options={
                'ordering': ['-creado'],
            },
        ),
        migrations.CreateModel(
            name='AforoTanque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel', models.IntegerField(blank=True, null=True)),
                ('metros', models.FloatField(blank=True, max_length=7, null=True)),
                ('centimetros', models.FloatField(blank=True, max_length=7, null=True)),
                ('milimetros', models.FloatField(blank=True, max_length=7, null=True)),
                ('um', models.IntegerField(blank=True, null=True, verbose_name='Usuario que modifica')),
                ('tanque', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bun.tanque')),
                ('uc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario que Crea')),
            ],
        ),
    ]
