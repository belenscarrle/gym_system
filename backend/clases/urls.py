# clases/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClaseViewSet, 
    HorarioViewSet, 
    ReservaViewSet, 
    ListaEsperaViewSet
)

router = DefaultRouter()
router.register(r'clases', ClaseViewSet)
router.register(r'horarios', HorarioViewSet)
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'lista-espera', ListaEsperaViewSet, basename='lista-espera')

urlpatterns = [
    path('', include(router.urls)),
]