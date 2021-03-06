from django import forms
from .models import TanqueBar, CalculoBar, LoteBar, CalculoPruebasBar, LoteApiBar, CalculoApiBar


class TanqueForm(forms.ModelForm):
    class Meta:
        model = TanqueBar
        exclude = ['creado', 'actualizado', 'uc', 'um', 'terminal']


class CalculoForm(forms.ModelForm):
    class Meta:
        model = CalculoBar
        exclude = ['creado', 'actualizado', 'uc', 'um', 'volumen', 'densidad', 'masa', 'api', 'tabla_6d','tabla_13']


class CalculoForm2(forms.ModelForm):
    class Meta:
        model = CalculoBar
        exclude = ['creado', 'actualizado', 'uc', 'um', 'densidad', 'volumen', 'masa']


class LoteForm(forms.ModelForm):
    class Meta:
        model = LoteBar
        exclude = ['creado', 'actualizado', 'uc', 'um']


class CalculoFormPruebasBar(forms.ModelForm):
    class Meta:
        model = CalculoPruebasBar
        exclude = ['creado', 'actualizado', 'uc', 'um', 'volumen', 'densidad', 'masa', 'api', 'tabla_6d','tabla_13']

class LoteApiFormBar(forms.ModelForm):
    class Meta:
        model = LoteApiBar
        exclude = ['creado', 'actualizado', 'uc', 'um']

class CalculoApiFormBar(forms.ModelForm):
    class Meta:
        model = CalculoApiBar
        exclude = ['creado', 'actualizado', 'uc', 'um','volumen', 'masa', 'densidad']