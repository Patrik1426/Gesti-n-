# backend/poa/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ObraViewSet

# El router crea automáticamente las URLs de la API
router = DefaultRouter()
router.register(r'obras', ObraViewSet, basename='obra')

urlpatterns = [
    path('', include(router.urls)),
]