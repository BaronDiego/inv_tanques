from datetime import date, datetime
from django.shortcuts import render, redirect
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
from .models import AforoTanqueCtg, CalculoCtg, TanqueCtg, LoteCtg, CalculoPruebasCtg
from .resources import AforoTanqueResourse
from .forms import CalculoForm, TanqueForm, LoteForm, CalculoForm2, CalculoFormPruebasCtg
from core.views import SinPrivilegios
import django_excel as excel
import locale
locale.setlocale(locale.LC_ALL, '')


@login_required(login_url='login')
@permission_required('ctg.add_aforotanquectg', login_url='sin_privilegios')
def importar(request):
    if request.method == 'POST':  
        aforo_resource = AforoTanqueResourse()
        dataset = Dataset()
        nuevos_aforos = request.FILES['xlsfile']
        try:
            imported_data = dataset.load(nuevos_aforos.read())
        except tablib.exceptions.UnsupportedFormat:
            messages.error(request, "El foramto del archivo no es compatible")
            return redirect('importar_ctg')

        result = aforo_resource.import_data(dataset, dry_run=True)

        if result.has_errors() or result.has_validation_errors():
            messages.error(request ,"Hay problemas con el archivo a cargar.")
            return redirect('importar_ctg')

        if not result.has_errors():
            aforo_resource.import_data(dataset, dry_run=False)

        return redirect('listado_tanques_ctg')
    return render(request, 'ctg/crear_tabla_aforo.html')


@login_required(login_url='login')
@permission_required('ctg.add_calculoctg', login_url='sin_privilegios')
def calculo(request):
    if request.method == 'POST':
        form = CalculoForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            medicion = cd['medicion']

            tanque = TanqueCtg.objects.filter(id=request.POST['tanque']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")

            temperatura_tanque = cd['temperatura_tq']
            lote = LoteCtg.objects.filter(id=request.POST['lote']).values()
            id_tanque = tanque[0]['id']
            densidad_ref = lote[0]['densidad_ref']
            temperatura_ref = lote[0]['temperatura_ref']
            factor_correccion = lote[0]['factor_correccion']
            
            medicion_aforo = AforoTanqueCtg.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = medicion_aforo[0]['medicion']
                form.instance.densidad = densidad_ref - ((temperatura_tanque-temperatura_ref)*factor_correccion)
                form.instance.masa = form.instance.densidad * form.instance.volumen
                form.instance.uc = request.user
                form.save()
                return redirect('listado_tanques_ope_ctg')
            except IndexError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque, o el valor de la medición esta fuera de rango")
                return redirect('importar_ctg')
            except TypeError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque")
                return redirect('importar_ctg')
                
    else:
        form = CalculoForm()
        return render(request, 'ctg/calcular.html', {'form':form})


@login_required(login_url='login')
@permission_required('ctg.add_calculoctg', login_url='sin_privilegios')
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

            tanque = TanqueCtg.objects.filter(id=request.POST['tanque']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")
            
            temperatura_tanque = cd['temperatura_tq']
            id_tanque = tanque[0]['id']
            medicion_aforo = AforoTanqueCtg.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = medicion_aforo[0]['medicion']
                galones = form.instance.volumen * 0.264172
                print(galones)
                galones_gsv = galones * tabla_6d
                print(galones_gsv)
                toneladas = float(tabla_13) * float(galones_gsv)
                print(toneladas)
                form.instance.uc = request.user
                form.instance.masa = toneladas
                form.save()
                return redirect('listado_tanques_ope')
            except IndexError:
                messages.error(request ,"El valor de la medición esta fuera de rango")
                return redirect('calcular_api')

    else:
        form = CalculoForm2()
        return render(request, 'ctg/calcular2.html', {'form':form})


class ListadoTanques( SinPrivilegios, ListView):
    permission_required = 'ctg.view_tanquectg'
    model = TanqueCtg
    template_name = 'ctg/listado_tanque.html'
    context_object_name = 'tanques_list'


@login_required(login_url='login')
def detalle_tanque(request, id):
    tanque = get_object_or_404(TanqueCtg, id=id)
    de_Tk = TanqueCtg.objects.filter(id=id).values()
    id_tanque = de_Tk[0]['id']
    tabla_aforo = AforoTanqueCtg.objects.filter(tanque_id=id_tanque)
    bandera_ta = False
    if tabla_aforo:
        bandera_ta = True
    
    return render(request, 'ctg/detalle_tanque.html', {'tanque':tanque, 'bandera_ta':bandera_ta, 'id_tanque':id_tanque})


class EditarTanque(SuccessMessageMixin, SinPrivilegios, UpdateView):
    permission_required = 'ctg.change_tanquectg'
    model = TanqueCtg
    form_class = TanqueForm
    template_name = 'ctg/editar_tanque.html'
    context_object_name = 'tanque_editar'
    success_url = reverse_lazy('listado_tanques_ctg')
    success_message = "Tanque editado correctamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class BorrarTanque( SuccessMessageMixin, SinPrivilegios, DeleteView):
    permission_required = 'ctg.delete_tanquectg'
    model = TanqueCtg
    template_name = 'ctg/borrar_tanque.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('listado_tanques_ctg')
    success_message = "Tanque elimiando satisfactoriamente"
    

@login_required(login_url='login')
def listado_tanques(request):
    qs_1 = CalculoCtg.objects.filter(creado__gte=date.today())
    qs_2 = TanqueCtg.objects.filter(id__in=Subquery(qs_1.values('tanque_id'))).values()
    hoy = date.today()
    return render(request, 'ctg/listado_tanque_operacion.html', {'qs_2':qs_2, 'hoy':hoy})


class CrearTanque( SinPrivilegios, CreateView):
    permission_required = 'ctg.add_tanquectg'
    model = TanqueCtg
    template_name = 'ctg/crear_tanque.html'
    success_url = reverse_lazy('listado_tanques_ctg')
    success_message = "Tanque creado satisfactoriamente"
    form_class = TanqueForm

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


@login_required(login_url='login')
def listado_calculos(request):
    idis_tk = TanqueCtg.objects.all().values_list('id')
    list_idis = []
    for id in idis_tk:
        list_idis.append(id[0])
    calculos = []
    for ct in list_idis:
        qs = CalculoCtg.objects.filter(tanque_id=ct).first()
        calculos.append(qs)
    return render(request, 'ctg/listado_calculo.html', {'calculos':calculos})


class CrearLote(SinPrivilegios, CreateView):
    permission_required = 'ctg.add_lotectg'
    model = LoteCtg
    template_name = 'ctg/crear_lote.html'
    success_url = reverse_lazy('listado_lotes_ctg')
    success_message = "Lote creado satisfactoriamente"
    form_class = LoteForm

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


class ListadoLote(SinPrivilegios, ListView):
    permission_required = 'ctg.view_lotectg'
    model = LoteCtg
    template_name = 'ctg/listado_lotes.html'
    context_object_name = 'lotes_list'


class DetalleLote(SinPrivilegios, DetailView):
    permission_required = 'ctg.view_lotectg'
    model = LoteCtg
    template_name = 'ctg/detalle_lote.html'
    context_object_name = 'de_Lt'


class EditarLote(SuccessMessageMixin, SinPrivilegios, UpdateView):
    permission_required = 'ctg.change_lotectg'
    model = LoteCtg
    form_class = LoteForm
    template_name = 'ctg/editar_lote.html'
    context_object_name = 'lote_editar'
    success_url = reverse_lazy('listado_lotes_ctg')
    success_message = "Lote editado correctamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class BorrarLote( SuccessMessageMixin, SinPrivilegios, DeleteView):
    permission_required = 'ctg.delete_lotectg'
    model = LoteCtg
    template_name = 'ctg/borrar_lote.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('listado_lotes_ctg')
    success_message = "Lote elimiando satisfactoriamente"


@login_required(login_url='login')
def detalle_ocupacion_tk(requeest, id):
    calculo = CalculoCtg.objects.filter(tanque_id=id).order_by('-creado')[:2]
    if calculo == "":
        calculo = 0
    calculo_tk = CalculoCtg.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
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
    
    lote = LoteCtg.objects.filter(id=calculo_lote).values()
    try:
        lote_producto = lote[0]['producto']
        lote_refencia = lote[0]['referencia']
        masa_tk = calculo_tk[0]['masa']
        # lote_buque = lote[0]['nombre_buque']
    except IndexError:
        lote_producto = 0
        masa_tk = 0

    tanque = TanqueCtg.objects.filter(id=id).values()
    tag = tanque[0]['tag']
    id_tk = tanque[0]['id']
    volumen_total_tk = tanque[0]['volumen']
    data = [volumen_total_tk, volumen_actual_tk]
    terminal = tanque[0]['terminal']

    try:
        porcentaje_ocupacion = (volumen_actual_tk / volumen_total_tk) * 100
    except TypeError:
        porcentaje_ocupacion = 0
    

    return render(requeest, 'ctg/detalle_ocupacion_tk.html', {
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
        'terminal':terminal
        })


def exportar_excel(request, id):
    export = []

    export.append(['Fecha', 'Tipo Medición','Medicion','Temperatua','Volumen', 'Densidad', 'Masa','Lote', 'Operador', 'Sellos Válvulas', 'Sellos Tapas','Nombre Buque']) #SellosValvulas - SellosTapas
    data = CalculoCtg.objects.filter(tanque_id=id)
    tanque = TanqueCtg.objects.filter(id=id).values()
    tag = tanque[0]['tag']


    for d in data:
        if d.estado == 'C':
            d.estado = 'Control'
        elif d.estado == 'D':
            d.estado = 'Definitiva'
        elif d.estado == 'F':
            d.estado = 'Final'
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
@permission_required('ctg.add_calculopruebasctg', login_url='sin_privilegios')
def calculo_pruebas_ctg(request):
    if request.method == 'POST':
        form = CalculoFormPruebasCtg(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if cd['medicion'] == None:
                cd['medicion'] = 0
            

            medicion = cd['medicion']

            tanque = TanqueCtg.objects.filter(id=request.POST['tanque']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")

            temperatura_tanque = cd['temperatura_tq']
            lote = LoteCtg.objects.filter(id=request.POST['lote']).values()
            id_tanque = tanque[0]['id']
            densidad_ref = lote[0]['densidad_ref']
            temperatura_ref = lote[0]['temperatura_ref']
            factor_correccion = lote[0]['factor_correccion']
            
            medicion_aforo = AforoTanqueCtg.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = medicion_aforo[0]['medicion']
                form.instance.densidad = densidad_ref - ((temperatura_tanque-temperatura_ref)*factor_correccion)
                form.instance.masa = form.instance.densidad * form.instance.volumen
                form.instance.uc = request.user
                form.save()
                return redirect('detalle_ocupacion_tk_pruebas_ctg')
            except IndexError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque, o el valor de la medición esta fuera de rango")
                return redirect('importar_ctg')
            except TypeError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque")
                return redirect('importar_ctg')
                
    else:
        form = CalculoFormPruebasCtg()
        return render(request, 'ctg/calcular_pruebas.html', {'form':form})


@login_required(login_url='login')
def detalle_ocupacion_tk_pruebas(requeest, id):
    calculo = CalculoPruebasCtg.objects.filter(tanque_id=id).order_by('-creado')[:2]
    if calculo == "" or calculo == 0:
        calculo = 0
    calculo_tk = CalculoPruebasCtg.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
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
    
    lote = LoteCtg.objects.filter(id=calculo_lote).values()
    try:
        lote_producto = lote[0]['producto']
        lote_refencia = lote[0]['referencia']
        masa_tk = calculo_tk[0]['masa']
        # lote_buque = lote[0]['nombre_buque']
    except IndexError:
        lote_producto = 0
        masa_tk = 0

    tanque = TanqueCtg.objects.filter(id=id).values()
    tag = tanque[0]['tag']
    id_tk = tanque[0]['id']
    volumen_total_tk = tanque[0]['volumen']
    data = [volumen_total_tk, volumen_actual_tk]
    terminal = tanque[0]['terminal']

    try:
        porcentaje_ocupacion = (volumen_actual_tk / volumen_total_tk) * 100
    except TypeError:
        porcentaje_ocupacion = 0
    

    return render(requeest, 'ctg/detalle_ocupacion_tk_pruebas.html', {
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
    qs_1 = CalculoPruebasCtg.objects.filter(creado__gte=date.today())
    qs_2 = TanqueCtg.objects.filter(id__in=Subquery(qs_1.values('tanque_id'))).values()
    print(qs_2)
    hoy = date.today()
    print(hoy)
    return render(request, 'ctg/listado_tanque_operacion_pruebas.html', {'qs_2':qs_2, 'hoy':hoy})


@login_required(login_url='login')
def enviar_data_erp(request, id):
    calculo = CalculoCtg.objects.filter(tanque_id=id).order_by('-creado')[:2]
    if calculo == "" or calculo == 0:
        calculo = 0
    calculo_tk = CalculoCtg.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
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
    
    lote = LoteCtg.objects.filter(id=calculo_lote).values()
    try:
        lote_producto = lote[0]['producto']
        lote_refencia = lote[0]['referencia']
        masa_tk = calculo_tk[0]['masa']
        # lote_buque = lote[0]['nombre_buque']
    except IndexError:
        lote_producto = 0
        masa_tk = 0

    tanque = TanqueCtg.objects.filter(id=id).values()
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
    

    return render(request, 'ctg/data_post.html', {'r':r, 'cantidad':masa_tk_str})


@login_required(login_url='login')
def detalle_tanque_sin_tabla_aforo(request):
    idis_tk = TanqueCtg.objects.all().values_list('id')
    list_idis = []
    for id in idis_tk:
        list_idis.append(id)

    con_tabla = []
    for i in list_idis:
        qs = AforoTanqueCtg.objects.filter(tanque_id=i).first()
        con_tabla.append(qs)
    
    print(con_tabla)

    return render(request, 'ctg/con_tabla.html', {'con_tabla':con_tabla})

