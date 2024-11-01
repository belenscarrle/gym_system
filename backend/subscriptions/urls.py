from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlanSuscripcionViewSet,
    SuscripcionViewSet,
    PagoViewSet
)

router = DefaultRouter()
router.register(r'planes', PlanSuscripcionViewSet, basename='plan')
router.register(r'suscripciones', SuscripcionViewSet, basename='suscripcion')
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [
    path('', include(router.urls)),
]