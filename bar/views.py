from datetime import date, datetime
from django.shortcuts import render, redirect
from tablib import Dataset
import tablib
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Subquery
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import AforoTanqueBar, CalculoBar, TanqueBar, LoteBar
from .resources import AforoTanqueResourse
from .forms import CalculoForm, TanqueForm, LoteForm, CalculoForm2
from core.views import SinPrivilegios
import django_excel as excel
import locale
locale.setlocale(locale.LC_ALL, '')


@login_required(login_url='login')
@permission_required('bar.add_aforotanque', login_url='sin_privilegios')
def importar(request):
    if request.method == 'POST':  
        aforo_resource = AforoTanqueResourse()
        dataset = Dataset()
        nuevos_aforos = request.FILES['xlsfile']
        try:
            imported_data = dataset.load(nuevos_aforos.read())
        except tablib.exceptions.UnsupportedFormat:
            messages.error(request, "El foramto del archivo no es compatible")

        result = aforo_resource.import_data(dataset, dry_run=True)

        if result.has_errors() or result.has_validation_errors():
            messages.error(request ,"Hay problemas con el archivo a cargar.")

        if not result.has_errors():
            aforo_resource.import_data(dataset, dry_run=False)

        return redirect('listado_tanques_bar')
    return render(request, 'bar/crear_tabla_aforo.html')


@login_required(login_url='login')
@permission_required('bar.add_calculo', login_url='sin_privilegios')
def calculo(request):
    if request.method == 'POST':
        form = CalculoForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if cd['medicion'] == None:
                cd['medicion'] = 0
            medicion = cd['medicion']

            tanque = TanqueBar.objects.filter(id=request.POST['tanque']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")

            temperatura_tanque = cd['temperatura_tq']
            lote = LoteBar.objects.filter(id=request.POST['lote']).values()
            id_tanque = tanque[0]['id']
            densidad_ref = lote[0]['densidad_ref']
            temperatura_ref = lote[0]['temperatura_ref']
            factor_correccion = lote[0]['factor_correccion']
            
            medicion_aforo = AforoTanqueBar.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = medicion_aforo[0]['medicion']
                form.instance.densidad = densidad_ref - ((temperatura_tanque-temperatura_ref)*factor_correccion)
                form.instance.masa = form.instance.densidad * form.instance.volumen
                form.instance.uc = request.user
                form.save()
                return redirect('listado_tanques_ope_bar')
            except IndexError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque, o el valor de la medición esta fuera de rango")
                return redirect('importar_bar')
            except TypeError:
                messages.error(request ,"No hay tabla de aforo cargada para este tanque")
                return redirect('importar_bar')
                
    else:
        form = CalculoForm()
        return render(request, 'bar/calcular.html', {'form':form})


@login_required(login_url='login')
@permission_required('bar.add_calculo', login_url='sin_privilegios')
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

            tanque = TanqueBar.objects.filter(id=request.POST['tanque']).values()
            altura_medicion_tanque = tanque[0]['altura_medicion']

            if medicion > altura_medicion_tanque:
                messages.error(request ,"La medición es mayor que la altura de medición estabelecida")
            
            temperatura_tanque = cd['temperatura_tq']
            id_tanque = tanque[0]['id']
            medicion_aforo = AforoTanqueBar.objects.filter(tanque_id=id_tanque, nivel=medicion).values()

            try:
                form.instance.volumen = medicion_aforo[0]['medicion']
                galones = form.instance.volumen * 0.264172
                galones_gsv = galones * tabla_6d
                toneladas = float(tabla_13) * float(galones_gsv)
                form.instance.uc = request.user
                form.instance.masa = toneladas
                form.save()
                return redirect('listado_tanques_ope_bar')
            except IndexError:
                messages.error(request ,"El valor de la medición esta fuera de rango")
                return redirect('calcular_api_bar')

    else:
        form = CalculoForm2()
        return render(request, 'bar/calcular2.html', {'form':form})


class ListadoTanques( SinPrivilegios, ListView):
    permission_required = 'bar.view_tanque'
    model = TanqueBar
    template_name = 'ctg/listado_tanque.html'
    context_object_name = 'tanques_list'


@login_required(login_url='login')
def detalle_tanque(request, id):
    tanque = get_object_or_404(TanqueBar, id=id)
    de_Tk = TanqueBar.objects.filter(id=id).values()
    id_tanque = de_Tk[0]['id']
    tabla_aforo = AforoTanqueBar.objects.filter(tanque_id=id_tanque)
    bandera_ta = False
    if tabla_aforo:
        bandera_ta = True
    
    return render(request, 'bar/detalle_tanque.html', {'tanque':tanque, 'bandera_ta':bandera_ta, 'id_tanque':id_tanque})


class EditarTanque(SuccessMessageMixin, SinPrivilegios, UpdateView):
    permission_required = 'bar.change_tanque'
    model = TanqueBar
    form_class = TanqueForm
    template_name = 'bar/editar_tanque.html'
    context_object_name = 'tanque_editar'
    success_url = reverse_lazy('listado_tanques_bar')
    success_message = "Tanque editado correctamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class BorrarTanque( SuccessMessageMixin, SinPrivilegios, DeleteView):
    permission_required = 'bar.delete_tanque'
    model = TanqueBar
    template_name = 'bar/borrar_tanque.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('listado_tanques_bar')
    success_message = "Proyecto elimiando satisfactoriamente"
    

@login_required(login_url='login')
def listado_tanques(request):
    qs_1 = CalculoBar.objects.filter(creado__gte=date.today())
    qs_2 = TanqueBar.objects.filter(id__in=Subquery(qs_1.values('tanque_id'))).values()
    hoy = date.today()
    return render(request, 'bar/listado_tanque_operacion.html', {'qs_2':qs_2, 'hoy':hoy})


class CrearTanque( SinPrivilegios, CreateView):
    permission_required = 'bar.add_tanque'
    model = TanqueBar
    template_name = 'bar/crear_tanque.html'
    success_url = reverse_lazy('listado_tanques_bar')
    form_class = TanqueForm

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


@login_required(login_url='login')
def listado_calculos(request):
    calculos = CalculoBar.objects.all()
    return render(request, 'bar/listado_calculo.html', {'calculos':calculos})


class CrearLote(SinPrivilegios, CreateView):
    permission_required = 'bar.add_lote'
    model = LoteBar
    template_name = 'bar/crear_lote.html'
    success_url = reverse_lazy('listado_lotes_bar')
    form_class = LoteForm

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


class ListadoLote(SinPrivilegios, ListView):
    permission_required = 'bar.view_lote'
    model = LoteBar
    template_name = 'bar/listado_lotes.html'
    context_object_name = 'lotes_list'


class DetalleLote(SinPrivilegios, DetailView):
    permission_required = 'bar.view_lote'
    model = LoteBar
    template_name = 'ctg/detalle_lote.html'
    context_object_name = 'de_Lt'


class EditarLote(SuccessMessageMixin, SinPrivilegios, UpdateView):
    permission_required = 'bar.change_lote'
    model = LoteBar
    form_class = LoteForm
    template_name = 'bar/editar_lote.html'
    context_object_name = 'lote_editar'
    success_url = reverse_lazy('listado_lotes_bar')
    success_message = "Lote editado correctamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class BorrarLote( SuccessMessageMixin, SinPrivilegios, DeleteView):
    permission_required = 'bar.delete_lote'
    model = LoteBar
    template_name = 'bar/borrar_lote.html'
    context_object_name = 'obj'
    success_url = reverse_lazy('listado_lotes_bar')
    success_message = "Lote elimiando satisfactoriamente"


@login_required(login_url='login')
def detalle_ocupacion_tk(requeest, id):
    calculo = CalculoBar.objects.filter(tanque_id=id).order_by('-creado')[:2]
    if calculo == "":
        calculo = 0
    calculo_tk = CalculoBar.objects.filter(tanque_id=id).order_by('-creado').values()[:1]
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
    
    lote = LoteBar.objects.filter(id=calculo_lote).values()
    try:
        lote_producto = lote[0]['producto']
        lote_refencia = lote[0]['referencia']
        masa_tk = calculo_tk[0]['masa']
        # lote_buque = lote[0]['nombre_buque']
    except IndexError:
        lote_producto = 0
        masa_tk = 0

    tanque = TanqueBar.objects.filter(id=id).values()
    tag = tanque[0]['tag']
    id_tk = tanque[0]['id']
    volumen_total_tk = tanque[0]['volumen']
    data = [volumen_total_tk, volumen_actual_tk]
    terminal = tanque[0]['terminal']

    try:
        porcentaje_ocupacion = (volumen_actual_tk / volumen_total_tk) * 100
    except TypeError:
        porcentaje_ocupacion = 0
    

    return render(requeest, 'bar/detalle_ocupacion_tk.html', {
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
    data = CalculoBar.objects.filter(tanque_id=id)
    tanque = TanqueBar.objects.filter(id=id).values()
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

