# subscriptions/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import PlanSuscripcion, Suscripcion, Pago
from .serializers import (
    PlanSuscripcionSerializer,
    SuscripcionSerializer,
    PagoSerializer,
    CrearSuscripcionSerializer
)

class PlanSuscripcionViewSet(viewsets.ModelViewSet):
    queryset = PlanSuscripcion.objects.filter(activo=True)
    serializer_class = PlanSuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class SuscripcionViewSet(viewsets.ModelViewSet):
    serializer_class = SuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Suscripcion.objects.all()
        return Suscripcion.objects.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearSuscripcionSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        suscripcion = self.get_object()
        if suscripcion.estado == 'ACTIVA':
            suscripcion.estado = 'CANCELADA'
            suscripcion.save()
            return Response({'status': 'Suscripción cancelada'})
        return Response(
            {'error': 'No se puede cancelar esta suscripción'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        plan = serializer.validated_data['plan']
        fecha_inicio = timezone.now()
        fecha_fin = fecha_inicio + timezone.timedelta(days=plan.duracion_dias)
        
        serializer.save(
            usuario=self.request.user,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            clases_restantes=plan.clases_disponibles
        )

class PagoViewSet(viewsets.ModelViewSet):
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Pago.objects.all()
        return Pago.objects.filter(suscripcion__usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def confirmar_pago(self, request, pk=None):
        pago = self.get_object()
        if pago.estado == 'PENDIENTE':
            pago.estado = 'COMPLETADO'
            pago.fecha_pago = timezone.now()
            pago.save()
            
            # Actualizar estado de la suscripción
            suscripcion = pago.suscripcion
            suscripcion.estado = 'ACTIVA'
            suscripcion.save()
            
            return Response({'status': 'Pago confirmado'})
        return Response(
            {'error': 'No se puede confirmar este pago'},
            status=status.HTTP_400_BAD_REQUEST
        )