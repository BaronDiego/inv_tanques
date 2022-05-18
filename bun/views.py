from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect
from pytz import utc
from tablib import Dataset
import tablib
from requests import post
import json
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Subquery
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.db.models import Q
from .models import AforoTanque, Calculo, Tanque, Lote, CalculoPruebas, LoteApi, CalculoApi
from .resources import AforoTanqueResourse
from .forms import CalculoForm, TanqueForm, LoteForm, CalculoForm2, CalculoFormPruebas, LoteApiForm, CalculoApiForm
from core.views import SinPrivilegios
import django_excel as excel
import locale
locale.setlocale(locale.LC_ALL, '')


@login_required(login_url='login')
@permission_required('bun.add_aforotanque', login_url='sin_privilegios')
def importar(request):
    if request.method == 'POST':  
        aforo_resource = AforoTanqueResourse()
        dataset = Dataset()
        nuevos_aforos = request.FILES['xlsfile']
        try:
            imported_data = dataset.load(nuevos_aforos.read())
        except tablib.exceptions.UnsupportedFormat:
            messages.error(request, "El foramto del archivo no es compatible")
            return redirect('importar')

        result = aforo_resource.import_data(dataset, dry_run=True)

        if result.has_errors() or result.has_validation_errors():
            messages.error(request ,"Hay problemas con el archivo a cargar.")
            return redirect('importar')

        if not result.has_errors():
            aforo_resource.import_data(dataset, dry_run=False)

        return redirect('listado_tanques')
    return render(request, 'bun/crear_tabla_aforo.html')


@login_required(login_url='login')
@permission_required('bun.add_calculo', login_url='sin_privilegios')
def calculo(request):
    if request.method == 'POST':
        form = CalculoForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            medicion = cd['medicion']

            tanque = Tanque.objects.filter(id=request.POST['tanque']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")

            temperatura_tanque = cd['temperatura_tq']
            lote = Lote.objects.filter(id=request.POST['lote']).values()
            id_tanque = tanque[0]['id']
            densidad_ref = lote[0]['densidad_ref']
            temperatura_ref = lote[0]['temperatura_ref']
            factor_correccion = lote[0]['factor_correccion']
            
            medicion_aforo = AforoTanque.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = int(medicion_aforo[0]['medicion'])
                form.instance.densidad = densidad_ref - ((temperatura_tanque-temperatura_ref)*factor_correccion)
                form.instance.masa = int(form.instance.densidad * form.instance.volumen) 
                form.instance.uc = request.user
                form.save()
                return redirect('listado_tanques_ope')
            except IndexError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque, o el valor de la medición esta fuera de rango")
                return redirect('importar')
            except TypeError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque")
                return redirect('importar')
                
    else:
        form = CalculoForm()
        return render(request, 'bun/calcular.html', {'form':form})


@login_required(login_url='login')
@permission_required('bun.add_calculo', login_url='sin_privilegios')
def crearCalculoApi(request):
    if request.method == 'POST':
        form = CalculoForm2(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['medicion'] == None:
                cd['medicion'] = 0
            medicion = cd['medicion']
            tabla_6d = cd['tabla_6d']
            tabla_13 = cd['tabla_13']

            tanque = Tanque.objects.filter(id=request.POST['tanque']).values()
            lote = Lote.objects.filter(id=request.POST['lote']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']
            densidad_ref = lote[0]['densidad_ref']
            temperatura_ref = lote[0]['temperatura_ref']
            factor_correccion = lote[0]['factor_correccion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")
            
            temperatura_tanque = cd['temperatura_tq']
            id_tanque = tanque[0]['id']
            medicion_aforo = AforoTanque.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = medicion_aforo[0]['medicion']
                form.instance.densidad = densidad_ref - ((temperatura_tanque-temperatura_ref)*factor_correccion)
                galones = form.instance.volumen * 0.264172
                galones_gsv = galones * tabla_6d
                toneladas = float(tabla_13) * float(galones_gsv)
                form.instance.uc = request.user
                form.instance.masa = toneladas
                form.save()
                return redirect('listado_tanques_ope')
            except IndexError:
                messages.error(request ,"El valor de la medición esta fuera de rango")
                return redirect('calcular_api')

    else:
        form = CalculoForm2()
        return render(request, 'bun/calcular2.html', {'form':form})


class ListadoTanques( SinPrivilegios, ListView):
    permission_required = 'bun.view_tanque'
    model = Tanque
    template_name = 'bun/listado_tanque.html'
    context_object_name = 'tanques_list'


@login_required(login_url='login')
def detalle_tanque(request, id):
    tanque = get_object_or_404(Tanque, id=id)
    de_Tk = Tanque.objects.filter(id=id).values()
    id_tanque = de_Tk[0]['id']
    tag = de_Tk[0]['tag']
    tabla_aforo = AforoTanque.objects.filter(tanque_id=id_tanque)
    bandera_ta = False
    if tabla_aforo:
        bandera_ta = True

    try:
        hoy = date.today()
        ultima_fecha = Calculo.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
        fecha = ultima_fecha[0]['creado']
        fecha_format = datetime.strftime(fecha,'%Y-%m-%d')
        fecha_a_fecha = datetime.strptime(fecha_format, '%Y-%m-%d').date()

        
        if (hoy - fecha_a_fecha) > timedelta(days=20):
            send_mail(
                '¡Alerta Tanque!', 
                'El tanque {} no se ha medido en los últimos 20 días'.format(tag), 
                'djangopruebas7@gmail.com', 
                ['diegoivanbaron@gmail.com', 'diego.baron@algranel.com.co'], 
                fail_silently=False
            )
    except IndexError:
        print("No hay calculos")

    
    return render(request, 'bun/detalle_tanque.html', {'tanque':tanque, 'bandera_ta':bandera_ta, 'id_tanque':id_tanque})


class EditarTanque(SuccessMessageMixin, SinPrivilegios, UpdateView):
    permission_required = 'bun.change_tanque'
    model = Tanque
    form_class = TanqueForm
    template_name = 'bun/editar_tanque.html'
    context_object_name = 'tanque_editar'
    success_url = reverse_lazy('listado_tanques')
    success_message = "Tanque editado correctamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class BorrarTanque( SuccessMessageMixin, SinPrivilegios, DeleteView):
    permission_required = 'bun.delete_tanque'
    model = Tanque
    template_name = 'bun/borrar_tanque.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('listado_tanques')
    success_message = "Tanque elimiando satisfactoriamente"
    

@login_required(login_url='login')
def listado_tanques(request):
    qs_1 = Calculo.objects.filter(creado__gte=date.today())
    qs_2 = Tanque.objects.filter(id__in=Subquery(qs_1.values('tanque_id'))).values()
    qs_3 = CalculoApi.objects.filter(creado__gte=date.today())
    qs_4 = Tanque.objects.filter(id__in=Subquery(qs_3.values('tanque_id'))).values()
    hoy = date.today()
    return render(request, 'bun/listado_tanque_operacion.html', {'qs_2':qs_2, 'qs_4':qs_4,'hoy':hoy})


class CrearTanque( SinPrivilegios, CreateView):
    permission_required = 'bun.add_tanque'
    model = Tanque
    template_name = 'bun/crear_tanque.html'
    success_url = reverse_lazy('listado_tanques')
    form_class = TanqueForm

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


@login_required(login_url='login')
def listado_calculos(request):
    idis_tk = Tanque.objects.all().values_list('id')
    list_idis = []
    for id in idis_tk:
        list_idis.append(id[0])
    calculos = []
    for ct in list_idis:
        qs = Calculo.objects.filter(tanque_id=ct).first()
        calculos.append(qs)
    return render(request, 'bun/listado_calculo.html', {'calculos':calculos})


class CrearLote(SinPrivilegios, CreateView):
    permission_required = 'bun.add_lote'
    model = Lote
    template_name = 'bun/crear_lote.html'
    success_url = reverse_lazy('listado_lotes')
    success_message = "Lote creado satisfactoriamente"
    form_class = LoteForm

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)

class ListadoLote(SinPrivilegios, ListView):
    permission_required = 'bun.view_lote'
    model = Lote
    template_name = 'bun/listado_lotes.html'
    context_object_name = 'lotes_list'


class DetalleLote(SinPrivilegios, DetailView):
    permission_required = 'bun.view_lote'
    model = Lote
    template_name = 'bun/detalle_lote.html'
    context_object_name = 'de_Lt'


class EditarLote(SuccessMessageMixin, SinPrivilegios, UpdateView):
    permission_required = 'bun.change_lote'
    model = Lote
    form_class = LoteForm
    template_name = 'bun/editar_lote.html'
    context_object_name = 'lote_editar'
    success_url = reverse_lazy('listado_lotes')
    success_message = "Lote editado correctamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class BorrarLote( SuccessMessageMixin, SinPrivilegios, DeleteView):
    permission_required = 'bun.delete_lote'
    model = Lote
    template_name = 'bun/borrar_lote.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('listado_lotes')
    success_message = "Lote elimiando satisfactoriamente"


@login_required(login_url='login')
def detalle_ocupacion_tk(request, id):
    creado_medicion_normal = Calculo.objects.filter(tanque_id=id).values().first()
    if creado_medicion_normal == None:
        fecha_ult_medicion = datetime(2000, 1, 1, 00, 00, 0, 209258, tzinfo=utc)
    else:
        fecha_ult_medicion =  creado_medicion_normal['creado']
    
    creado_medicion_api = CalculoApi.objects.filter(tanque_id=id).values().first()
    if creado_medicion_api == None:
        fecha_ult_medicion_api = datetime(2000, 1, 1, 00, 00, 0, 209258, tzinfo=utc)
    else:
        fecha_ult_medicion_api =  creado_medicion_api['creado']

    if fecha_ult_medicion_api > fecha_ult_medicion:
        calculo_api = CalculoApi.objects.filter(tanque_id=id).order_by('-creado')[:2]
        if calculo_api == "" or calculo_api == 0:
            calculo_api = 0
        calculo_tk_api = CalculoApi.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
        if calculo_tk_api == "":
            calculo_tk_api = 0
        # volumen_actual_tk = calculo_tk[0]['volumen']
        try:
            volumen_actual_tk_api = calculo_tk_api[0]['volumen']
            ultima_medicion_api = calculo_tk_api[0]['creado']
            calculo_lote_api = calculo_tk_api[0]['lote_id']
            tipo_medicion_api = calculo_tk_api[0]['estado']
        except IndexError:
            volumen_actual_tk_api = 0
            ultima_medicion_api = 0
            calculo_lote_api = 0
        
        lote_api = LoteApi.objects.filter(id=calculo_lote_api).values()
        try:
            lote_producto_api = lote_api[0]['producto']
            lote_refencia_api = lote_api[0]['referencia']
            masa_tk_api = calculo_tk_api[0]['masa']
            # lote_buque = lote[0]['nombre_buque']
        except IndexError:
            lote_producto_api = 0
            masa_tk_api = 0

        tanque_api = Tanque.objects.filter(id=id).values()
        tag_api = tanque_api[0]['tag']
        id_tk_api = tanque_api[0]['id']
        volumen_total_tk_api = tanque_api[0]['volumen']
        data_api = [volumen_total_tk_api, volumen_actual_tk_api]
        terminal_api = tanque_api[0]['terminal']
        bodega_api = tanque_api[0]['bodega']
        tipo_api = tanque_api[0]['tipo']
        diametro_api = tanque_api[0]['diametro']
        altura_cilindro_api = tanque_api[0]['altura_cilindro']

        try:
            porcentaje_ocupacion_api = (volumen_actual_tk_api / volumen_total_tk_api) * 100
        except TypeError:
            porcentaje_ocupacion_api = 0
        
        return render(request, 'bun/detalle_ocupacion_tk_api.html', {
            'mediciones':calculo_api, 
            'volumen_total_tk':volumen_total_tk_api,
            'volumen_actual_tk':volumen_actual_tk_api,
            'lote_producto':lote_producto_api,
            'masa_tk':masa_tk_api,
            'data':data_api,
            'tag':tag_api,
            'ultima_medicion':ultima_medicion_api,
            'porcentaje_ocupacion':porcentaje_ocupacion_api,
            'id_tk':id_tk_api,
            'lote_refencia':lote_refencia_api,
            'tipo_medicion':tipo_medicion_api,
            'terminal':terminal_api,
            'tipo':tipo_api,
            'diametro':diametro_api,
            'altura_cilindro':altura_cilindro_api
            })
    else:
        calculo = Calculo.objects.filter(tanque_id=id).order_by('-creado')[:2]
        if calculo == "" or calculo == 0:
            calculo = 0
        calculo_tk = Calculo.objects.filter(tanque_id=id).order_by('-creado').values()[:1]

        try:
            id_calculo = calculo_tk[0]['id']
        except IndexError:
            id_calculo = 0
        
        if calculo_tk == "":
            calculo_tk = 0
        # volumen_actual_tk = calculo_tk[0]['volumen'] 
        try:
            volumen_actual_tk = calculo_tk[0]['volumen']
            ultima_medicion = calculo_tk[0]['creado']
            calculo_lote = calculo_tk[0]['lote_id']
            tipo_medicion = calculo_tk[0]['estado']
            creado = calculo_tk[0]['creado']
        except IndexError:
            volumen_actual_tk = 0
            ultima_medicion = 0
            calculo_lote = 0
            tipo_medicion = "-"
        
        lote = Lote.objects.filter(id=calculo_lote).values()
        try:
            lote_producto = lote[0]['producto']
            lote_refencia = lote[0]['referencia']
            masa_tk = calculo_tk[0]['masa']
            # lote_buque = lote[0]['nombre_buque']
        except IndexError:
            lote_producto = 0
            masa_tk = 0
            lote_refencia = "-"

        tanque = Tanque.objects.filter(id=id).values()
        tag = tanque[0]['tag']
        id_tk = tanque[0]['id']
        volumen_total_tk = tanque[0]['volumen']
        data = [volumen_total_tk, volumen_actual_tk]
        terminal = tanque[0]['terminal']
        bodega = tanque[0]['bodega']
        tipo = tanque[0]['tipo']
        diametro = tanque[0]['diametro']
        altura_cilindro = tanque[0]['altura_cilindro']

        try:
            porcentaje_ocupacion = (volumen_actual_tk / volumen_total_tk) * 100
        except TypeError:
            porcentaje_ocupacion = 0

        return render(request, 'bun/detalle_ocupacion_tk.html', {
            'mediciones':calculo, 
            'volumen_total_tk':volumen_total_tk,
            'volumen_actual_tk':volumen_actual_tk,
            'lote_producto':lote_producto,
            'masa_tk':masa_tk,
            'data':data,
            'tag':tag,
            'ultima_medicion':ultima_medicion,
            'porcentaje_ocupacion':porcentaje_ocupacion,
            'id_tk':id_tk,
            'lote_refencia':lote_refencia,
            'tipo_medicion':tipo_medicion,
            'terminal':terminal,
            'id_calculo':id_calculo,
            'tipo':tipo,
            'diametro':diametro,
            'altura_cilindro':altura_cilindro

            })



@login_required(login_url='login')
def exportar_excel(request, id):
    export = []

    export.append(['Fecha', 'Tipo Medición','Medicion','Temperatua','Volumen', 'Densidad', 'Masa','Lote', 'Operador', 'Sellos Válvulas', 'Sellos Tapas','Nombre Buque', 'Fecha Llegada Buque']) #SellosValvulas - SellosTapas
    data = Calculo.objects.filter(tanque_id=id)
    tanque = Tanque.objects.filter(id=id).values()
    tag = tanque[0]['tag']


    for d in data:
        if d.estado == 'C':
            d.estado = 'Control'
        elif d.estado == 'D':
            d.estado = 'Definitiva'
        elif d.estado == 'F':
            d.estado = 'Final'
        elif d.estado == 'ID':
            d.estado = 'Inicial Despacho'
        elif d.estado == 'IR':
            d.estado = 'Inicial Recibo'
        elif d.estado == 'FD':
            d.estado = 'Final Despacho'
        elif d.estado == 'FR':
            d.estado = 'Final Recibo'
        else:
            d.estado = 'Inicial'


        try:
            export.append([
                "{0:%Y-%m-%d}".format(d.creado),
                d.estado.upper(),
                d.medicion,
                d.temperatura_tq,
                d.volumen,
                d.densidad,
                d.masa,
                d.lote.producto.upper(),
                d.uc.username.upper(),
                d.sellos_valvulas,
                d.sellos_tapas,
                d.lote.nombre_buque.upper(),
                d.lote.fecha_llegada_buque
            ])
        except AttributeError:
          return redirect('listado_tanques')

    today    = datetime.now()
    strToday = today.strftime("%Y%m%d")
    sheet = excel.pe.Sheet(export)

    return excel.make_response(sheet, "xlsx", file_name="data"+tag+"_"+strToday+".xlsx")


@login_required(login_url='login')
@permission_required('bun.add_calculopruebas', login_url='sin_privilegios')
def calculo_pruebas(request):
    if request.method == 'POST':
        form = CalculoFormPruebas(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if cd['medicion'] == None:
                cd['medicion'] = 0
            

            medicion = cd['medicion']

            tanque = Tanque.objects.filter(id=request.POST['tanque']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")

            temperatura_tanque = cd['temperatura_tq']
            lote = Lote.objects.filter(id=request.POST['lote']).values()
            id_tanque = tanque[0]['id']
            densidad_ref = lote[0]['densidad_ref']
            temperatura_ref = lote[0]['temperatura_ref']
            factor_correccion = lote[0]['factor_correccion']
            
            medicion_aforo = AforoTanque.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = medicion_aforo[0]['medicion']
                form.instance.densidad = densidad_ref - ((temperatura_tanque-temperatura_ref)*factor_correccion)
                form.instance.masa = form.instance.densidad * form.instance.volumen
                form.instance.uc = request.user
                form.save()
                return redirect('listado_tanques_ope_pruebas')
            except IndexError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque, o el valor de la medición esta fuera de rango")
                return redirect('importar')
            except TypeError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque")
                return redirect('importar')
                
    else:
        form = CalculoFormPruebas()
        return render(request, 'bun/calcular_pruebas.html', {'form':form})


@login_required(login_url='login')
def detalle_ocupacion_tk_pruebas(requeest, id):
    calculo = CalculoPruebas.objects.filter(tanque_id=id).order_by('-creado')[:2]
    if calculo == "" or calculo == 0:
        calculo = 0
    calculo_tk = CalculoPruebas.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
    if calculo_tk == "":
        calculo_tk = 0
    # volumen_actual_tk = calculo_tk[0]['volumen']
    try:
        volumen_actual_tk = calculo_tk[0]['volumen']
        ultima_medicion = calculo_tk[0]['creado']
        calculo_lote = calculo_tk[0]['lote_id']
    except IndexError:
        volumen_actual_tk = 0
        ultima_medicion = 0
        calculo_lote = 0
    
    lote = Lote.objects.filter(id=calculo_lote).values()
    try:
        lote_producto = lote[0]['producto']
        lote_refencia = lote[0]['referencia']
        masa_tk = calculo_tk[0]['masa']
        # lote_buque = lote[0]['nombre_buque']
    except IndexError:
        lote_producto = 0
        masa_tk = 0

    tanque = Tanque.objects.filter(id=id).values()
    tag = tanque[0]['tag']
    id_tk = tanque[0]['id']
    volumen_total_tk = tanque[0]['volumen']
    data = [volumen_total_tk, volumen_actual_tk]
    terminal = tanque[0]['terminal']

    try:
        porcentaje_ocupacion = (volumen_actual_tk / volumen_total_tk) * 100
    except TypeError:
        porcentaje_ocupacion = 0
    

    return render(requeest, 'bun/detalle_ocupacion_tk_pruebas.html', {
        'mediciones':calculo, 
        'volumen_total_tk':volumen_total_tk,
        'volumen_actual_tk':volumen_actual_tk,
        'lote_producto':lote_producto,
        'masa_tk':masa_tk,
        'data':data,
        'tag':tag,
        'ultima_medicion':ultima_medicion,
        'porcentaje_ocupacion':porcentaje_ocupacion,
        'id_tk':id_tk,
        'lote_refencia':lote_refencia,
        'terminal':terminal
        })


@login_required(login_url='login')
def listado_tanques_pruebas(request):
    qs_1 = CalculoPruebas.objects.filter(creado__gte=date.today())
    qs_2 = Tanque.objects.filter(id__in=Subquery(qs_1.values('tanque_id'))).values()
    print(qs_2)
    hoy = date.today()
    print(hoy)
    return render(request, 'bun/listado_tanque_operacion_pruebas.html', {'qs_2':qs_2, 'hoy':hoy})


@login_required(login_url='login')
def enviar_data_erp(request, id):
    calculo = Calculo.objects.filter(tanque_id=id).order_by('-creado')[:2]
    if calculo == "" or calculo == 0:
        calculo = 0
    calculo_tk = Calculo.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
    if calculo_tk == "":
        calculo_tk = 0
    # volumen_actual_tk = calculo_tk[0]['volumen'] 
    try:
        ultima_medicion = calculo_tk[0]['creado']
        calculo_lote = calculo_tk[0]['lote_id']
        tipo_medicion = calculo_tk[0]['estado']
        creado = calculo_tk[0]['creado']
    except IndexError:
        volumen_actual_tk = 0
        ultima_medicion = 0
        calculo_lote = 0
    
    lote = Lote.objects.filter(id=calculo_lote).values()
    try:
        lote_producto = lote[0]['producto']
        lote_refencia = lote[0]['referencia']
        masa_tk = calculo_tk[0]['masa']
        # lote_buque = lote[0]['nombre_buque']
    except IndexError:
        lote_producto = 0
        masa_tk = 0

    tanque = Tanque.objects.filter(id=id).values()
    tag = tanque[0]['tag']
    id_tk = tanque[0]['id']
    terminal = tanque[0]['terminal']
    bodega = tanque[0]['bodega']
    masa_tk_str = int(masa_tk)
    hoy = date.today()
    hoy2=hoy.strftime("%y%m%d")
    
    ### Enviar cantidad a SIESA ###
    url = "http://localhost/api_GTIntegration/api/algranel/ajusteInventario"
    datos = {
        "ajuste": {
            "f350_id_co": "002",
            "f350_id_tipo_docto": "AJM",
            "f350_consec_docto": "1",
            "f350_fecha": hoy2,
            "f350_id_tercero": "",
            "f350_notas": "TEST api",
            "f450_docto_alterno": "INDO7461",
            "movimiento": [
            {
                "f470_id_co": "002",
                "f470_id_tipo_docto": "AJM",
                "f470_consec_docto": "1",
                "f470_nro_registro": "1",
                "f470_id_bodega": bodega,
                "f470_id_ubicacion_aux": tag,
                "f470_id_lote": lote_refencia,
                "f470_id_motivo": "",
                "f470_id_co_movto": "002",
                "f470_id_ccosto_movto": "",
                "f470_id_unidad_medida": "KG",
                "f470_cant_base": masa_tk_str,
                "f470_costo_prom_uni": "",
                "f470_notas": "TEST API",
                "f470_referencia_item": lote_producto,
                "f470_id_un_movto": "001"
            }
            ]
        },
        "f_cia": "1"
    }

    headers = {"content-type": "application/json"}

    r = post(url=url, data=json.dumps(datos), headers=headers)
    print(r)
    if r.status_code == 200:
        messages.success(request,"La cantidad {} ha sido guardada correctamente en la ERP".format(masa_tk_str))
    else:
        messages.error(request,"Hay un error al guadar la cantidad")
    

    return render(request, 'bun/data_post.html', {'r':r, 'cantidad':masa_tk_str})

@login_required(login_url='login')
def detalle_tanque_sin_tabla_aforo(request):
    idis_tk = Tanque.objects.all().values_list('id')
    list_idis = []
    for id in idis_tk:
        list_idis.append(id)

    con_tabla = []
    for i in list_idis:
        qs = AforoTanque.objects.filter(tanque_id=i).first()
        con_tabla.append(qs)
    
    print(con_tabla)

    return render(request, 'bun/con_tabla.html', {'con_tabla':con_tabla})


@login_required(login_url='login')
@permission_required('bun.add_calculoapi', login_url='sin_privilegios')
def calculoApi(request):
    if request.method == 'POST':
        form = CalculoApiForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['medicion'] == None:
                cd['medicion'] = 0
            medicion = cd['medicion']
            tabla_6d = cd['tabla_6d']

            tanque = Tanque.objects.filter(id=request.POST['tanque']).values()
            lote = LoteApi.objects.filter(id=request.POST['lote']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']
            temperatura = lote[0]['temperatura']
            api = lote[0]['api']


            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")

            id_tanque = tanque[0]['id']
            medicion_aforo = AforoTanque.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            form.instance.volumen = medicion_aforo[0]['medicion']
            galones = form.instance.volumen * 0.264172
            masa1 = galones * tabla_6d
            tabla13 = ((141.3819577/(api + 131.5)) - 0.001199407795) * 3.785411784
            form.instance.masa = masa1 * tabla13
            try:
                form.instance.densidad = form.instance.masa / form.instance.volumen
            except ZeroDivisionError:
                form.instance.densidad = 0
            form.instance.uc = request.user
            form.save()
            return redirect('listado_tanques_ope')
    else:
        form = CalculoApiForm()
        return render(request, 'bun/calcularApi.html', {'form':form})


class CrearLoteApi(SinPrivilegios, CreateView):
    permission_required = 'bun.add_loteapi'
    model = LoteApi
    template_name = 'bun/crear_lote_api.html'
    success_url = reverse_lazy('listado_lotes')
    form_class = LoteApiForm

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)

class ListadoLoteApi(SinPrivilegios, ListView):
    permission_required = 'bun.view_loteapi'
    model = LoteApi
    template_name = 'bun/listado_lotes_api.html'
    context_object_name = 'lotes_list_api'

class DetalleLoteApi(SinPrivilegios, DetailView):
    permission_required = 'bun.view_loteapi'
    model = LoteApi
    template_name = 'bun/detalle_lote_api.html'
    context_object_name = 'obj'

class EditarLoteApi(SuccessMessageMixin, SinPrivilegios, UpdateView):
    permission_required = 'bun.change_loteapi'
    model = LoteApi
    form_class = LoteApiForm
    template_name = 'bun/editar_lote_api.html'
    context_object_name = 'lote_editar'
    success_url = reverse_lazy('listado_lotes_api')
    success_message = "Lote editado correctamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class BorrarLoteApi( SuccessMessageMixin, SinPrivilegios, DeleteView):
    permission_required = 'bun.delete_loteapi'
    model = LoteApi
    template_name = 'bun/borrar_lote_api.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('listado_lotes_api')
    success_message = "Lote elimiando satisfactoriamente"


@login_required(login_url='login')
def detalle_ocupacion_tk_api(request, id):
    calculo = CalculoApi.objects.filter(tanque_id=id).order_by('-creado')[:2]
    if calculo == "" or calculo == 0:
        calculo = 0
    calculo_tk = CalculoApi.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
    if calculo_tk == "":
        calculo_tk = 0
    # volumen_actual_tk = calculo_tk[0]['volumen']
    try:
        volumen_actual_tk = calculo_tk[0]['volumen']
        ultima_medicion = calculo_tk[0]['creado']
        calculo_lote = calculo_tk[0]['lote_id']
        tipo_medicion = calculo_tk[0]['estado']
    except IndexError:
        volumen_actual_tk = 0
        ultima_medicion = 0
        calculo_lote = 0
    
    lote = LoteApi.objects.filter(id=calculo_lote).values()
    try:
        lote_producto = lote[0]['producto']
        lote_refencia = lote[0]['referencia']
        masa_tk = calculo_tk[0]['masa']
        # lote_buque = lote[0]['nombre_buque']
    except IndexError:
        lote_producto = 0
        masa_tk = 0

    tanque = Tanque.objects.filter(id=id).values()
    tag = tanque[0]['tag']
    id_tk = tanque[0]['id']
    volumen_total_tk = tanque[0]['volumen']
    data = [volumen_total_tk, volumen_actual_tk]
    terminal = tanque[0]['terminal']
    bodega = tanque[0]['bodega']
    tipo = tanque[0]['tipo']
    diametro = tanque[0]['diametro']
    altura_cilindro = tanque[0]['altura_cilindro']


    try:
        porcentaje_ocupacion = (volumen_actual_tk / volumen_total_tk) * 100
    except TypeError:
        porcentaje_ocupacion = 0
    

    return render(request, 'bun/detalle_ocupacion_tk_api.html', {
        'mediciones':calculo, 
        'volumen_total_tk':volumen_total_tk,
        'volumen_actual_tk':volumen_actual_tk,
        'lote_producto':lote_producto,
        'masa_tk':masa_tk,
        'data':data,
        'tag':tag,
        'ultima_medicion':ultima_medicion,
        'porcentaje_ocupacion':porcentaje_ocupacion,
        'id_tk':id_tk,
        'lote_refencia':lote_refencia,
        'tipo_medicion':tipo_medicion,
        'terminal':terminal,
        'tipo':tipo,
        'diametro':diametro,
        'altura_cilindro':altura_cilindro
        })


@login_required(login_url='login')
def exportar_excel_tanques(request):
    export = []
    export.append(['Tanque','Volumen Tanque (m3)','Masa (TON)','Cliente','Lote (DO)','Producto'])

    idis_tk = Tanque.objects.all().values()
    list_idis = []
    for id in idis_tk:
        list_idis.append(id['id'])

    calculos = []
    for ct in list_idis:
        qs = Calculo.objects.filter(tanque_id=ct).first()
        if qs:
            calculos.append(qs)

    for qs in calculos:
        if qs.masa == 0:
            qs.lote.cliente = "Sin cliente"
            qs.lote.producto = "Vacio"

        export.append([
            qs.tanque.tag,
            qs.tanque.volumen / 1000,
            qs.masa / 1000,
            qs.lote.cliente,
            qs.lote.referencia,
            qs.lote.producto.upper()
        ])


    today    = datetime.now()
    strToday = today.strftime("%Y%m%d")
    sheet = excel.pe.Sheet(export)
    return excel.make_response(sheet, "xlsx", file_name="dataTanquesBun"+"_"+strToday+".xlsx")


@login_required(login_url='login')
def exportar_excel_api(request, id):
    export = []

    export.append(['Fecha', 'Tipo Medición','Medicion','Temperatua','Volumen', 'Densidad', 'Masa','Lote-Api', 'Operador']) #SellosValvulas - SellosTapas
    data = CalculoApi.objects.filter(tanque_id=id)
    tanque = Tanque.objects.filter(id=id).values()
    tag = tanque[0]['tag']


    for d in data:
        if d.estado == 'C':
            d.estado = 'Control'
        elif d.estado == 'D':
            d.estado = 'Definitiva'
        elif d.estado == 'F':
            d.estado = 'Final'
        elif d.estado == 'ID':
            d.estado = 'Inicial Despacho'
        elif d.estado == 'IR':
            d.estado = 'Inicial Recibo'
        elif d.estado == 'FD':
            d.estado = 'Final Despacho'
        elif d.estado == 'FR':
            d.estado = 'Final Recibo'
        else:
            d.estado = 'Inicial'


        try:
            export.append([
                "{0:%Y-%m-%d}".format(d.creado),
                d.estado.upper(),
                d.medicion,
                d.temperatura_tq,
                "{:,.2f}".format(d.volumen).replace(",", "@").replace(".", ",").replace("@", "."),
                d.densidad,
                "{:,.2f}".format(d.masa).replace(",", "@").replace(".", ",").replace("@", "."),
                d.lote.producto.upper(),
                d.uc.username.upper(),
            ])
        except AttributeError:
          return redirect('listado_tanques')

    today    = datetime.now()
    strToday = today.strftime("%Y%m%d")
    sheet = excel.pe.Sheet(export)

    return excel.make_response(sheet, "xlsx", file_name="dataApi"+tag+"_"+strToday+".xlsx")


@login_required(login_url='login')
def buscar_lote(request):
    q = request.GET.get('q', '')
    querys = (Q(referencia__icontains=q ) | Q(producto__icontains=q))
    lotes = Lote.objects.filter(querys)
    cantidad = lotes.count()
    return render(request, 'bun/buscar_lote.html', {
        'lotes':lotes, 
        'cantidad':cantidad,
        'q':q
        })


@login_required(login_url='login')
def buscar_tanque(request):
    q = request.GET.get('q', '')
    querys = (Q(bodega__icontains=q ) | Q(tag__icontains=q))
    tanques = Tanque.objects.filter(querys)
    cantidad = tanques.count()
    return render(request, 'bun/buscar_tanque.html', {
        'tanques':tanques, 
        'cantidad':cantidad,
        'q':q
        })


@login_required(login_url='login')
def buscar_lote_api(request):
    q = request.GET.get('q', '')
    querys = (Q(referencia__icontains=q ) | Q(producto__icontains=q))
    lotes = LoteApi.objects.filter(querys)
    cantidad = lotes.count()
    return render(request, 'bun/buscar_lote_api.html', {
        'lotes':lotes, 
        'cantidad':cantidad,
        'q':q
        })
