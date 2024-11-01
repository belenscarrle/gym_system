# clases/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import ListaEspera
from .serializers import ListaEsperaSerializer
from .models import Clase, Horario, Reserva
from .serializers import ClaseSerializer, HorarioSerializer, ReservaSerializer

class ClaseViewSet(viewsets.ModelViewSet):
    queryset = Clase.objects.all()
    serializer_class = ClaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['get'])
    def horarios(self, request, pk=None):
        clase = self.get_object()
        horarios = clase.horarios.all()
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data)

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def reservar(self, request, pk=None):
        horario = self.get_object()
        fecha = request.data.get('fecha')
        
        if not fecha:
            return Response(
                {'error': 'Debe especificar una fecha'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reserva = Reserva.objects.create(
                usuario=request.user,
                horario=horario,
                fecha=fecha,
                estado='confirmada'
            )
            serializer = ReservaSerializer(reserva)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user, estado='confirmada')

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        reserva = self.get_object()
        if reserva.fecha <= timezone.now().date():
            return Response(
                {'error': 'No se pueden cancelar reservas pasadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.estado = 'cancelada'
        reserva.save()
        return Response({'status': 'Reserva cancelada'})

    def perform_destroy(self, instance):
        with transaction.atomic():
            # Marcar la reserva como cancelada
            instance.estado = 'cancelada'
            instance.save()

            # Buscar el primer usuario en lista de espera
            lista_espera = ListaEspera.objects.filter(
                horario=instance.horario,
                fecha=instance.fecha,
                estado='pendiente'
            ).order_by('posicion').first()

            if lista_espera:
                lista_espera.promocionar()

class ListaEsperaViewSet(viewsets.ModelViewSet):
    serializer_class = ListaEsperaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ListaEspera.objects.filter(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        horario = request.data.get('horario')
        fecha = request.data.get('fecha')

        # Verificar si ya existe una reserva o está en lista de espera
        if Reserva.objects.filter(
            usuario=request.user,
            horario_id=horario,
            fecha=fecha,
            estado='confirmada'
        ).exists():
            return Response(
                {'error': 'Ya tienes una reserva para esta clase'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if ListaEspera.objects.filter(
            usuario=request.user,
            horario_id=horario,
            fecha=fecha,
            estado='pendiente'
        ).exists():
            return Response(
                {'error': 'Ya estás en la lista de espera para esta clase'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        lista_espera = self.get_object()
        if lista_espera.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden cancelar registros pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Actualizar estado
            lista_espera.estado = 'cancelado'
            lista_espera.save()

            # Reordenar posiciones
            ListaEspera.objects.filter(
                horario=lista_espera.horario,
                fecha=lista_espera.fecha,
                estado='pendiente',
                posicion__gt=lista_espera.posicion
            ).update(posicion=F('posicion') - 1)

        return Response({'status': 'Registro en lista de espera cancelado'}) 