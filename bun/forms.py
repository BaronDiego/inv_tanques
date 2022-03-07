from django import forms
from .models import Tanque, Calculo, Lote, CalculoPruebas, LoteApi, CalculoApi


class TanqueForm(forms.ModelForm):
    class Meta:
        model = Tanque
        exclude = ['creado', 'actualizado', 'uc', 'um', 'terminal']


class CalculoForm(forms.ModelForm):
    class Meta:
        model = Calculo
        exclude = ['creado', 'actualizado', 'uc', 'um', 'volumen', 'densidad', 'masa', 'api', 'tabla_6d','tabla_13']


class CalculoForm2(forms.ModelForm):
    class Meta:
        model = Calculo
        exclude = ['creado', 'actualizado', 'uc', 'um', 'densidad', 'volumen', 'masa']


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        exclude = ['creado', 'actualizado', 'uc', 'um']

class CalculoFormPruebas(forms.ModelForm):
    class Meta:
        model = CalculoPruebas
        exclude = ['creado', 'actualizado', 'uc', 'um', 'volumen', 'densidad', 'masa', 'api', 'tabla_6d','tabla_13']


class LoteApiForm(forms.ModelForm):
    class Meta:
        model = LoteApi
        exclude = ['creado', 'actualizado', 'uc', 'um']

class CalculoApiForm(forms.ModelForm):
    class Meta:
        model = CalculoApi
        exclude = ['creado', 'actualizado', 'uc', 'um','volumen', 'masa', 'densidad']