from django.db import models
from django.contrib.auth.models import User

# Create your models here.
TIPO_MEDIDA = (
    ('F', 'FINAL'),
    ('I', 'INICIAL'),
    ('C', 'CONTROL'),
    ('D', 'DEFINITIVA'),
    ('ID', 'INICIAL DESPACHO'),
    ('IR', 'INICIAL RECIBO'),
    ('FD', 'FINAL DESPACHO'),
    ('FR', 'FINAL RECIBO'),
)

class ClaseBase(models.Model):
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    uc = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que Crea")
    um = models.IntegerField(blank=True, null=True, verbose_name="Usuario que modifica")

    class Meta:
        abstract = True


class TanqueBar(ClaseBase):
    bodega= models.CharField(max_length=10, unique=True, null=True, blank=True)
    tag = models.CharField(max_length=50, unique=True)
    terminal = models.CharField(max_length=20, default="BARRANQUILLA")
    tipo = models.CharField(max_length=150)
    diametro = models.FloatField(max_length=6, verbose_name="Diámetro")
    altura_cilindro = models.FloatField(max_length=6)
    altura_medicion = models.FloatField(max_length=6, verbose_name="Altura medición")
    fecha_aforo = models.DateField()
    norma = models.CharField(max_length=150)
    volumen = models.FloatField(max_length=8, blank=True, null=True)

    def save(self):
        self.tag = self.tag.upper()
        super(TanqueBar, self).save()

    class Meta:
        ordering = ['bodega']

    def __str__(self):
        return self.tag
        

class AforoTanqueBar(models.Model):
    tanque = models.ForeignKey(TanqueBar, on_delete=models.CASCADE)
    nivel = models.IntegerField(blank=True, null=True)
    medicion = models.FloatField(max_length=7, blank=True, null=True)
    uc = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario que Crea")
    um = models.IntegerField(blank=True, null=True, verbose_name="Usuario que modifica")


class LoteBar(ClaseBase):
    referencia = models.CharField(max_length=50)
    producto = models.CharField(max_length=55)
    temperatura_ref = models.FloatField(max_length=4, blank=True, null=True)
    densidad_ref = models.FloatField(max_length=6, blank=True, null=True)
    factor_correccion = models.FloatField(max_length=6, blank=True, null=True, verbose_name="Factor corrección")
    nombre_buque = models.CharField(max_length=50, blank=True, null=True)
    fecha_llegada_buque = models.DateField(blank=True, null=True)
    cliente = models.CharField(max_length=100, blank=True, null=True, default="-")

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return "{} - {}".format(self.producto, self.referencia)

    def save(self):
        self.referencia = self.referencia.upper()
        self.producto = self.producto.upper()
        self.nombre_buque = self.nombre_buque.upper()
        super(LoteBar, self).save()


class CalculoBar(ClaseBase):
    tanque = models.ForeignKey(TanqueBar, on_delete=models.CASCADE, related_name='tanque')
    lote = models.ForeignKey(LoteBar, on_delete=models.CASCADE, null=True, related_name='lote')
    estado = models.CharField(max_length=2, choices=TIPO_MEDIDA)
    medicion = models.FloatField(max_length=7, blank=True, null=True, verbose_name="Medición" ,default=0)
    tabla_6d = models.FloatField(max_length=8, blank=True, null=True, default=0)
    tabla_13 = models.FloatField(max_length=8, blank=True, null=True, default=0)
    volumen = models.FloatField(max_length=8, blank=True, null=True)
    temperatura_tq = models.FloatField(max_length=4, blank=True, null=True)
    sellos_valvulas = models.CharField(max_length=150, blank=True, verbose_name="Sellos Válvulas")
    sellos_tapas = models.CharField(max_length=150, blank=True)
    densidad = models.FloatField(max_length=8, blank=True, null=True, default=0)
    masa = models.FloatField(max_length=8, blank=True, null=True)

    def ocupacion(self):
        try:
            ocupacion = (self.volumen / self.tanque.volumen) * 100
        except TypeError:
            ocupacion = 0
        except ZeroDivisionError:
            ocupacion = 0
        return ocupacion


    class Meta:
        ordering = ['-creado']

    def save(self):
        self.estado = self.estado.upper()
        self.sellos_valvulas = self.sellos_valvulas.upper()
        self.sellos_tapas = self.sellos_tapas.upper()
        super(CalculoBar, self).save()


class CalculoPruebasBar(ClaseBase):
    tanque = models.ForeignKey(TanqueBar, on_delete=models.CASCADE)
    lote = models.ForeignKey(LoteBar, on_delete=models.CASCADE, null=True, verbose_name="Referencia/Lote")
    medicion = models.FloatField(max_length=7, blank=True, null=True, verbose_name="Medición" ,default=0)
    tabla_6d = models.FloatField(max_length=8, blank=True, null=True, default=0)
    tabla_13 = models.FloatField(max_length=8, blank=True, null=True, default=0)
    volumen = models.FloatField(max_length=8, blank=True, null=True)
    temperatura_tq = models.FloatField(max_length=4, blank=True, null=True)
    sellos_valvulas = models.CharField(max_length=150, blank=True, verbose_name="Sellos Válvulas")
    sellos_tapas = models.CharField(max_length=150, blank=True)
    densidad = models.FloatField(max_length=8, blank=True, null=True, default=0)
    masa = models.FloatField(max_length=8, blank=True, null=True)


    class Meta:
        ordering = ['-creado']

    def save(self):
        self.sellos_valvulas = self.sellos_valvulas.upper()
        self.sellos_tapas = self.sellos_tapas.upper()
        super(CalculoPruebasBar, self).save()


class LoteApiBar(ClaseBase):
    referencia = models.CharField(max_length=20)
    producto = models.CharField(max_length=25)
    temperatura = models.FloatField(max_length=4)
    api = models.FloatField(max_length=4)
    cliente = models.CharField(max_length=100, blank=True, null=True, default="-")

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return "{} - {}".format(self.producto, self.referencia)

    def save(self):
        self.referencia = self.referencia.upper()
        self.producto = self.producto.upper()
        super(LoteApiBar, self).save()


class CalculoApiBar(ClaseBase):
    tanque = models.ForeignKey(TanqueBar, on_delete=models.CASCADE)
    lote_api = models.ForeignKey(LoteApiBar, on_delete=models.CASCADE, related_name='lote_api')
    medicion = models.FloatField(max_length=7, verbose_name="Medición" ,default=0)
    tabla_6d = models.FloatField(max_length=7)
    volumen = models.FloatField(max_length=8, blank=True, null=True)
    masa = models.FloatField(max_length=8, blank=True, null=True)
    estado = models.CharField(max_length=2, choices=TIPO_MEDIDA)
    temperatura_tq = models.FloatField(max_length=4, blank=True, null=True)
    densidad = models.FloatField(max_length=8, blank=True, null=True, default=0)

    class Meta:
        ordering = ['-creado']







