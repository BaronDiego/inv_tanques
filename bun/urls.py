from django.urls import path
from . import views

urlpatterns = [
    path('calcular/', views.calculo, name='calcular'),
    path('listado_tanques_operacion/', views.listado_tanques, name='listado_tanques_ope'),
    path('listado_tanques/', views.ListadoTanques.as_view(), name='listado_tanques'),
    path('detalle_tanques_ocupacion/<int:id>/', views.detalle_tanque, name='detalle_tanque_ocu'),
    path('crear_tanque/', views.CrearTanque.as_view(), name='crear_tanque'),
    path('listado_ocupacion_tanques/', views.listado_calculos, name='listado_calculos'),
    path('crear_lote/', views.CrearLote.as_view(), name='crear_lote'),
    path('importar_ta/',views.importar, name='importar'),
    path('detalle_ocupacion_tk/<int:id>/', views.detalle_ocupacion_tk, name='detalle_ocupacion_tk'),
    path('exportar_excel/<int:id>/', views.exportar_excel, name='exportar_excel'),
    path('detalle_tanque/<int:id>/', views.detalle_tanque, name='detalle_tanque'),
    path('editar_tanque/<pk>/', views.EditarTanque.as_view(), name='editar_tanque'),
    path('eliminar_tanque/<pk>/', views.BorrarTanque.as_view(), name='eliminar_tanque'),
    path('listado_lotes/', views.ListadoLote.as_view(), name='listado_lotes'),
    path('editar_lote/<pk>/', views.EditarLote.as_view(), name='editar_lote'),
    path('detalle_lote/<pk>/', views.DetalleLote.as_view(), name='detalle_lote'),
    path('eliminar_lote/<pk>/', views.BorrarLote.as_view(), name='eliminar_lote'),
    path('calcular_api/', views.crearCalculoApi, name='calcular_api'),
    path('calcular_pruebas/', views.calculo_pruebas, name='calcular_pruebas'),
    path('detalle_ocupacion_tk_pruebas/<int:id>/', views.detalle_ocupacion_tk_pruebas, name='detalle_ocupacion_tk_pruebas'),
    path('listado_tanques_operacion_pruebas/', views.listado_tanques_pruebas, name='listado_tanques_ope_pruebas'),
]
