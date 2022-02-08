from django.urls import path
from . import views

urlpatterns = [
    path('calcular/', views.calculo, name='calcular_bar'),
    path('listado_tanques_operacion/', views.listado_tanques, name='listado_tanques_ope_bar'),
    path('listado_tanques/', views.ListadoTanques.as_view(), name='listado_tanques_bar'),
    path('detalle_tanques_ocupacion/<int:id>/', views.detalle_tanque, name='detalle_tanque_ocu_bar'),
    path('crear_tanque/', views.CrearTanque.as_view(), name='crear_tanque_bar'),
    path('listado_ocupacion_tanques/', views.listado_calculos, name='listado_calculos_bar'),
    path('crear_lote/', views.CrearLote.as_view(), name='crear_lote_bar'),
    path('importar_ta/',views.importar, name='importar_bar'),
    path('detalle_ocupacion_tk/<int:id>/', views.detalle_ocupacion_tk, name='detalle_ocupacion_tk_bar'),
    path('exportar_excel/<int:id>/', views.exportar_excel, name='exportar_excel_bar'),
    path('detalle_tanque/<int:id>/', views.detalle_tanque, name='detalle_tanque_bar'),
    path('editar_tanque/<pk>/', views.EditarTanque.as_view(), name='editar_tanque_bar'),
    path('eliminar_tanque/<pk>/', views.BorrarTanque.as_view(), name='eliminar_tanque_bar'),
    path('listado_lotes/', views.ListadoLote.as_view(), name='listado_lotes_bar'),
    path('editar_lote/<pk>/', views.EditarLote.as_view(), name='editar_lote_bar'),
    path('detalle_lote/<pk>/', views.DetalleLote.as_view(), name='detalle_lote_bar'),
    path('eliminar_lote/<pk>/', views.BorrarLote.as_view(), name='eliminar_lote_bar'),
    path('calcular_api/', views.crearCalculoApi, name='calcular_api_bar'),
    path('enviar_data_erp_bar/<int:id>/', views.enviar_data_erp, name='enviar_data_erp_bar'),
]
