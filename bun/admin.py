from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Tanque, AforoTanque

# Register your models here.
admin.site.site_header = "Administración InvAlgranel"



@admin.register(Tanque)
class TanqueAdmin(admin.ModelAdmin):
    list_display = ['tag', 'tipo', 'diametro', 'altura_cilindro', 'altura_medicion', 'fecha_aforo', 'norma', 'creado', 'actualizado', 'uc', 'um']


@admin.register(AforoTanque)
class PersonAdmin(ImportExportModelAdmin):
    pass