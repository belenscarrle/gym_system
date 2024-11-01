# clases/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import F
import logging
logger = logging.getLogger(__name__)

User = get_user_model()

class Clase(models.Model):
    NIVEL_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    capacidad_maxima = models.PositiveIntegerField()
    duracion_minutos = models.PositiveIntegerField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clases_impartidas'
    )
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Clase'
        verbose_name_plural = 'Clases'

    def __str__(self):
        return f"{self.nombre} - {self.get_nivel_display()}"

class Horario(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    sala = models.CharField(max_length=50)
    cupos_disponibles = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['dia_semana', 'hora_inicio']

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin')
        if self.cupos_disponibles > self.clase.capacidad_maxima:
            raise ValidationError('Los cupos disponibles no pueden exceder la capacidad máxima de la clase')

    def __str__(self):
        return f"{self.clase.nombre} - {self.get_dia_semana_display()} {self.hora_inicio}"

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        unique_together = ['usuario', 'horario', 'fecha']
        ordering = ['-fecha', '-fecha_creacion']

    def clean(self):
        # Verificar que la fecha de reserva sea futura
        if self.fecha < timezone.now().date():
            raise ValidationError('No se pueden hacer reservas para fechas pasadas')
        
        # Verificar disponibilidad de cupos
        reservas_count = Reserva.objects.filter(
            horario=self.horario,
            fecha=self.fecha,
            estado='confirmada'
        ).count()
        
        if reservas_count >= self.horario.cupos_disponibles:
            raise ValidationError('No hay cupos disponibles para esta clase')

    def __str__(self):
        return f"{self.usuario.username} - {self.horario} - {self.fecha}"
    
class ListaEspera(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listas_espera')
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='lista_espera')
    fecha = models.DateField()
    posicion = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    notificado = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('promocionado', 'Promocionado'),
            ('expirado', 'Expirado'),
            ('cancelado', 'Cancelado')
        ],
        default='pendiente'
    )

    class Meta:
        verbose_name = 'Lista de Espera'
        verbose_name_plural = 'Listas de Espera'
        unique_together = ['usuario', 'horario', 'fecha']
        ordering = ['fecha', 'posicion']

    def save(self, *args, **kwargs):
        if not self.posicion:
            # Asignar la siguiente posición disponible
            ultima_posicion = ListaEspera.objects.filter(
                horario=self.horario,
                fecha=self.fecha,
                estado='pendiente'
            ).order_by('-posicion').first()
            
            self.posicion = (ultima_posicion.posicion + 1) if ultima_posicion else 1
        
        super().save(*args, **kwargs)

    def promocionar(self):
        """Promociona el usuario de la lista de espera a una reserva confirmada"""
        if self.estado != 'pendiente':
            raise ValidationError('Solo se pueden promocionar registros pendientes')

        try:
            with transaction.atomic():
                # Crear la reserva
                Reserva.objects.create(
                    usuario=self.usuario,
                    horario=self.horario,
                    fecha=self.fecha,
                    estado='confirmada'
                )
                
                # Actualizar estado en lista de espera
                self.estado = 'promocionado'
                self.save()

                # Reordenar las posiciones restantes
                ListaEspera.objects.filter(
                    horario=self.horario,
                    fecha=self.fecha,
                    estado='pendiente',
                    posicion__gt=self.posicion
                ).update(posicion=F('posicion') - 1)

                return True
        except Exception as e:
            logger.error(f"Error al promocionar desde lista de espera: {str(e)}")
            return False

    def __str__(self):
        return f"{self.usuario.username} - {self.horario} - Posición: {self.posicion}"