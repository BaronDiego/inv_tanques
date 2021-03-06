from django import forms
from .models import TanqueCtg, CalculoCtg, LoteCtg, CalculoPruebasCtg, LoteApiCtg, CalculoApiCtg


class TanqueForm(forms.ModelForm):
    class Meta:
        model = TanqueCtg
        exclude = ['creado', 'actualizado', 'uc', 'um', 'terminal']


class CalculoForm(forms.ModelForm):
    class Meta:
        model = CalculoCtg
        exclude = ['creado', 'actualizado', 'uc', 'um', 'volumen', 'densidad', 'masa', 'api', 'tabla_6d','tabla_13']


class CalculoForm2(forms.ModelForm):
    class Meta:
        model = CalculoCtg
        exclude = ['creado', 'actualizado', 'uc', 'um', 'densidad', 'volumen', 'masa']


class LoteForm(forms.ModelForm):
    class Meta:
        model = LoteCtg
        exclude = ['creado', 'actualizado', 'uc', 'um']

class CalculoFormPruebasCtg(forms.ModelForm):
    class Meta:
        model = CalculoPruebasCtg
        exclude = ['creado', 'actualizado', 'uc', 'um', 'volumen', 'densidad', 'masa', 'api', 'tabla_6d','tabla_13']

class LoteApiFormCtg(forms.ModelForm):
    class Meta:
        model = LoteApiCtg
        exclude = ['creado', 'actualizado', 'uc', 'um']

class CalculoApiFormCtg(forms.ModelForm):
    class Meta:
        model = CalculoApiCtg
        exclude = ['creado', 'actualizado', 'uc', 'um','volumen', 'masa', 'densidad']