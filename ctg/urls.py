from django.urls import path
from . import views

urlpatterns = [
    path('calcular/', views.calculo, name='calcular_ctg'),
    path('listado_tanques_operacion/', views.listado_tanques, name='listado_tanques_ope_ctg'),
    path('listado_tanques/', views.ListadoTanques.as_view(), name='listado_tanques_ctg'),
    path('detalle_tanques_ocupacion/<int:id>/', views.detalle_tanque, name='detalle_tanque_ocu_ctg'),
    path('crear_tanque/', views.CrearTanque.as_view(), name='crear_tanque_ctg'),
    path('listado_ocupacion_tanques/', views.listado_calculos, name='listado_calculos_ctg'),
    path('crear_lote/', views.CrearLote.as_view(), name='crear_lote_ctg'),
    path('importar_ta/',views.importar, name='importar_ctg'),
    path('detalle_ocupacion_tk/<int:id>/', views.detalle_ocupacion_tk, name='detalle_ocupacion_tk_ctg'),
    path('exportar_excel/<int:id>/', views.exportar_excel, name='exportar_excel_ctg'),
    path('detalle_tanque/<int:id>/', views.detalle_tanque, name='detalle_tanque_ctg'),
    path('editar_tanque/<pk>/', views.EditarTanque.as_view(), name='editar_tanque_ctg'),
    path('eliminar_tanque/<pk>/', views.BorrarTanque.as_view(), name='eliminar_tanque_ctg'),
    path('listado_lotes/', views.ListadoLote.as_view(), name='listado_lotes_ctg'),
    path('editar_lote/<pk>/', views.EditarLote.as_view(), name='editar_lote_ctg'),
    path('detalle_lote/<pk>/', views.DetalleLote.as_view(), name='detalle_lote_ctg'),
    path('eliminar_lote/<pk>/', views.BorrarLote.as_view(), name='eliminar_lote_ctg'),
    path('calcular_api/', views.calculoApiCtg, name='calcular_api_ctg'),
    path('calcular_pruebas/', views.calculo_pruebas_ctg, name='calcular_pruebas_ctg'),
    path('detalle_ocupacion_tk_pruebas/<int:id>/', views.detalle_ocupacion_tk_pruebas, name='detalle_ocupacion_tk_pruebas_ctg'),
    path('listado_tanques_operacion_pruebas/', views.listado_tanques_pruebas, name='listado_tanques_ope_pruebas_ctg'),
    path('enviar_data_erp_ctg/<int:id>/', views.enviar_data_erp, name='enviar_data_erp_ctg'),
    path('con_tabla/', views.detalle_tanque_sin_tabla_aforo, name='con_tabla_ctg'),
    path('calculo_api', views.calculoApiCtg, name="calculoApi_ctg"),
    path('crear_lote_api/', views.CrearLoteApiCtg.as_view(), name='crear_lote_api_ctg'),
    path('detalle_ocupacion_tk_api/<int:id>/', views.detalle_ocupacion_tk_api_ctg, name='detalle_ocupacion_tk_api_ctg'),
    path('exportar_excel_api/<int:id>/', views.exportar_excel_api, name='exportar_excel_api_ctg'),
    path('listado_lotes_api/', views.ListadoLoteApiCtg.as_view(), name='listado_lotes_api_ctg'),
    path('detalle_lote_api/<pk>/', views.DetalleLoteApiCtg.as_view(), name='detalle_lote_api_ctg'),
    path('buscar_lote', views.buscar_lote, name='buscar_lote_ctg'),
    path('buscar_tanque', views.buscar_tanque, name='buscar_tanque_ctg'),
    path('buscar_lote_api', views.buscar_lote_api, name='buscar_lote_api_ctg'),
    path('editar_lote_api/<pk>/', views.EditarLoteApiCtg.as_view(), name='editar_lote_api_ctg'),
    path('eliminar_lote_api/<pk>/', views.BorrarLoteApiCtg.as_view(), name='eliminar_lote_api_ctg'),
    path('exportar_tanques/', views.exportar_excel_tanques_ctg, name="exportar_excel_tanques_ctg"),
    path('enviar_data_erp_ctg_api/<int:id>/', views.enviar_data_erp_api_ctg, name='enviar_data_erp_ctg_api'),
]
