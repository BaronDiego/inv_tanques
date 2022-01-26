from rest_framework import serializers
from bun.models import Calculo, Lote, Tanque
from ctg.models import CalculoCtg, LoteCtg, TanqueCtg
from bar.models import CalculoBar, LoteBar, TanqueBar

class TanqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tanque
        fields = ['tag']


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = ['producto', 'referencia']


class CalculoSerializer(serializers.ModelSerializer):
    tanque = TanqueSerializer(read_only=True)
    tanqueId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Tanque.objects.all(), source='tanque')
    lote = LoteSerializer(read_only=True)
    loteId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Lote.objects.all(), source='lotes')
    class Meta:
        model = Calculo
        fields = ['id', 'masa', 'tanque', 'tanqueId', 'lote', 'loteId', 'creado']


class TanqueSerializerCtg(serializers.ModelSerializer):
    class Meta:
        model = TanqueCtg
        fields = ['tag']


class LoteSerializerCtg(serializers.ModelSerializer):
    class Meta:
        model = LoteCtg
        fields = ['producto', 'referencia']


class CalculoSerializerCtg(serializers.ModelSerializer):
    tanque = TanqueSerializerCtg(read_only=True)
    tanqueId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=TanqueCtg.objects.all(), source='tanque')
    lote = LoteSerializerCtg(read_only=True)
    loteId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=LoteCtg.objects.all(), source='lotes')
    class Meta:
        model = CalculoCtg
        fields = ['id', 'masa', 'tanque', 'tanqueId', 'lote', 'loteId', 'creado']


class TanqueSerializerBar(serializers.ModelSerializer):
    class Meta:
        model = TanqueBar
        fields = ['tag']


class LoteSerializerBar(serializers.ModelSerializer):
    class Meta:
        model = LoteBar
        fields = ['producto', 'referencia']


class CalculoSerializerBar(serializers.ModelSerializer):
    tanque = TanqueSerializerBar(read_only=True)
    tanqueId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=TanqueBar.objects.all(), source='tanque')
    lote = LoteSerializerBar(read_only=True)
    loteId = serializers.PrimaryKeyRelatedField(write_only=True, queryset=LoteBar.objects.all(), source='lotes')
    class Meta:
        model = CalculoBar
        fields = ['id', 'masa', 'tanque', 'tanqueId', 'lote', 'loteId', 'creado']




