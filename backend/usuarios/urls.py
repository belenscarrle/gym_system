from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# router para las vistas basadas en ViewSet
router = DefaultRouter()
router.register('', views.UsuarioViewSet, basename='usuario')

# Patrones de URL para la aplicación usuarios
urlpatterns = [
    path('', include(router.urls)),
]