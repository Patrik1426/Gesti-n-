from django.shortcuts import render

# Create your views here.
# backend/poa/views.py
from rest_framework import viewsets
from .models import Obra
from .serializers import ObraSerializer

class ObraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Obra.objects.all()
    serializer_class = ObraSerializer