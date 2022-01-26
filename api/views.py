from rest_framework import generics
from bun.models import Calculo, Lote
from ctg.models import CalculoCtg, LoteCtg
from bar.models import CalculoBar, LoteBar
from .serializers import CalculoSerializer, LoteSerializer, CalculoSerializerCtg, LoteSerializerBar, LoteSerializerCtg, CalculoSerializerBar


class SubjectListView(generics.ListAPIView):
    queryset = Calculo.objects.all()
    serializer_class = CalculoSerializer

    
class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer


class SubjectListViewCtg(generics.ListAPIView):
    queryset = CalculoCtg.objects.all()
    serializer_class = CalculoSerializerCtg

    
class SubjectDetailViewCtg(generics.RetrieveAPIView):
    queryset = LoteCtg.objects.all()
    serializer_class = LoteSerializerCtg


class SubjectListViewBar(generics.ListAPIView):
    queryset = CalculoBar.objects.all()
    serializer_class = CalculoSerializerBar

    
class SubjectDetailViewBar(generics.RetrieveAPIView):
    queryset = LoteBar.objects.all()
    serializer_class = LoteSerializerBar